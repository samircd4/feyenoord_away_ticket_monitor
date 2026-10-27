import io
import os
import sys
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
from rich import print

# Ensure UTF-8 output encoding for Windows terminals
if sys.platform == "win32":
    try:
        if isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout.reconfigure(encoding="utf-8")
        if isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Monitoring and Retry configurations
try:
    CHECK_INTERVAL_SECONDS = max(1, int(os.getenv("CHECK_INTERVAL_SECONDS", "10")))
except ValueError:
    CHECK_INTERVAL_SECONDS = 10

try:
    MAX_RETRIES = max(1, int(os.getenv("MAX_RETRIES", "3")))
except ValueError:
    MAX_RETRIES = 3

try:
    RETRY_DELAY_SECONDS = max(0.5, float(os.getenv("RETRY_DELAY_SECONDS", "2")))
except ValueError:
    RETRY_DELAY_SECONDS = 2.0

BASE_API_URL = "https://feyenoord.api.tymes4-infra.com"

BASE_HEADERS = {
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9,nl;q=0.8',
    'Connection': 'keep-alive',
    'Origin': 'https://tickets.feyenoord.com',
    'Referer': 'https://tickets.feyenoord.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
}


def get_valid_token(
    current_token: str | None = None,
    max_retries: int = MAX_RETRIES,
    retry_delay: float = RETRY_DELAY_SECONDS,
) -> str:
    """
    Fetches a new valid token or refreshes an existing one from Tymes4 API with retry logic.
    """
    url = f"{BASE_API_URL}/v2/Account/ensure-valid-token"
    headers = {**BASE_HEADERS}
    if current_token:
        headers['Authorization'] = f"Bearer {current_token}"

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            token = data.get("Token")
            if not token:
                raise ValueError("Could not obtain token from ensure-valid-token response.")
            return str(token)
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                print(
                    f"[yellow]⚠️ Failed to fetch token (attempt {attempt}/{max_retries}): {e}. "
                    f"Retrying in {retry_delay}s...[/yellow]"
                )
                time.sleep(retry_delay)
            else:
                print(f"[red]❌ Failed to fetch token after {max_retries} attempts: {e}[/red]")

    raise RuntimeError(f"Unable to obtain valid token after {max_retries} attempts: {last_error}")


def send_telegram_notification(
    bot_token: str,
    chat_id: str,
    message: str,
    max_retries: int = MAX_RETRIES,
    retry_delay: float = RETRY_DELAY_SECONDS,
) -> bool:
    """
    Sends a message via Telegram Bot API using HTML formatting with retry logic.
    """
    if not bot_token or not chat_id:
        print("[yellow]! Telegram bot token or chat ID is missing in .env. Notification skipped.[/yellow]")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=10)
            res_data = response.json()
            if res_data.get("ok"):
                print("[green]✔ Telegram notification sent successfully![/green]")
                return True
            else:
                error_desc = res_data.get("description", "Unknown error")
                print(f"[red]❌ Telegram API error: {error_desc}[/red]")
                # Rate limit handling: wait for required cooldown
                if response.status_code == 429:
                    retry_after = res_data.get("parameters", {}).get("retry_after", retry_delay)
                    print(f"[yellow]Telegram rate limited. Waiting {retry_after}s before retry...[/yellow]")
                    time.sleep(retry_after)
                    continue
                return False
        except Exception as e:
            if attempt < max_retries:
                print(
                    f"[yellow]⚠️ Telegram notification failed (attempt {attempt}/{max_retries}): {e}. "
                    f"Retrying in {retry_delay}s...[/yellow]"
                )
                time.sleep(retry_delay)
            else:
                print(f"[red]❌ Telegram notification failed after {max_retries} attempts: {e}[/red]")
                return False

    return False


def fetch_events(
    token: str,
    max_retries: int = MAX_RETRIES,
    retry_delay: float = RETRY_DELAY_SECONDS,
) -> tuple[dict, str]:
    """
    Fetches event data using the provided token with retry logic.
    Automatically refreshes token if expired (401 Unauthorized).
    Returns a tuple of (events_data, active_token).
    """
    url = f"{BASE_API_URL}/v2/Event"
    active_token = token
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        headers = {
            **BASE_HEADERS,
            'Authorization': f'Bearer {active_token}',
            'no-auth': 'true',
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)

            # If expired or unauthorized, refresh token and retry immediately
            if resp.status_code == 401:
                print("[yellow]🔄 Token expired. Obtaining a new token...[/yellow]")
                active_token = get_valid_token(max_retries=max_retries, retry_delay=retry_delay)
                headers['Authorization'] = f'Bearer {active_token}'
                resp = requests.get(url, headers=headers, timeout=10)

            resp.raise_for_status()
            return resp.json(), active_token
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                print(
                    f"[yellow]⚠️ Failed to fetch events (attempt {attempt}/{max_retries}): {e}. "
                    f"Retrying in {retry_delay}s...[/yellow]"
                )
                time.sleep(retry_delay)
            else:
                print(f"[red]❌ Failed to fetch events after {max_retries} attempts: {e}[/red]")

    raise RuntimeError(f"Unable to fetch events after {max_retries} attempts: {last_error}")


def check_away_matches(
    token: str | None,
    notified_events: set[str],
    max_retries: int = MAX_RETRIES,
    retry_delay: float = RETRY_DELAY_SECONDS,
) -> str | None:
    """
    Executes a single check cycle for Away Match tickets.
    Deduplicates notifications to avoid spamming the user every interval.
    Returns the active token for reuse in the next cycle.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[bold blue]=== [{now_str}] Checking Away Match Events ===[/bold blue]")

    # Obtain token if we don't already have one
    if not token:
        print("[cyan]Fetching valid token from Feyenoord Ticketshop...[/cyan]")
        token = get_valid_token(max_retries=max_retries, retry_delay=retry_delay)

    data, active_token = fetch_events(token, max_retries=max_retries, retry_delay=retry_delay)

    away_tab = next(
        (tab for tab in data.get("TabItems", []) if tab.get("CategoryId") == 3), None
    )

    if not away_tab:
        print("[yellow]No Away Match tab (CategoryId=3) found in response.[/yellow]")
        return active_token

    items = away_tab.get("Items", [])
    if not items:
        print("[yellow]No away match items currently listed.[/yellow]")
        return active_token

    current_cycle_available_ids: set[str] = set()

    for event in items:
        event_name = str(event.get("Name", "Unknown Match"))
        event_id = str(event.get("Id", event_name))
        event_date = event.get("EventStartDateTime", "N/A")
        has_tickets = event.get("HasTicketsAvailable", False)
        button_data = event.get("ButtonData") or {}
        button_code = button_data.get("TranslationCode")
        button_style = button_data.get("ButtonStyle")
        deep_link = event.get("DeepLinkRoute") or "https://tickets.feyenoord.com"

        # Condition for available tickets to buy
        is_available_to_buy = bool(has_tickets and button_style != "Disabled")
        status_text = "🟢 AVAILABLE TO BUY" if is_available_to_buy else "🔴 NOT AVAILABLE"

        print(f"Match: {event_name}")
        print(f"  - Has Tickets Available: {has_tickets}")
        print(f"  - Button Translation Code: {button_code}")
        print(f"  - Status: {status_text}")
        print("-" * 40)

        if is_available_to_buy:
            current_cycle_available_ids.add(event_id)

            # Send notification ONLY if not already notified during this availability window
            if event_id not in notified_events:
                message = (
                    f"🎟️ <b>Ticket Available to Buy!</b>\n\n"
                    f"⚽ <b>Match:</b> {event_name}\n"
                    f"📅 <b>Date:</b> {event_date}\n"
                    f"🔘 <b>Button:</b> {button_code}\n"
                    f"🔗 <a href=\"{deep_link}\">Purchase Tickets Here</a>"
                )
                print(f"[bold green]🔔 Sending Telegram alert for: {event_name}[/bold green]")
                success = send_telegram_notification(
                    TELEGRAM_BOT_TOKEN,
                    TELEGRAM_CHAT_ID,
                    message,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                )
                if success:
                    notified_events.add(event_id)
            else:
                print(f"[dim green]ℹ️ Alert already sent previously for: {event_name}[/dim green]")

    # If an event previously had tickets and is now sold out / no longer available,
    # remove it from notified_events so a new alert can trigger if it restocks
    cleared_events = notified_events - current_cycle_available_ids
    for cleared_id in cleared_events:
        notified_events.remove(cleared_id)

    return active_token


def main():
    """
    Main loop that runs the ticket monitor continuously based on CHECK_INTERVAL_SECONDS.
    """
    print("[bold green]====================================================[/bold green]")
    print("[bold green]       Feyenoord Away Ticket Monitor Started        [/bold green]")
    print("[bold green]====================================================[/bold green]")
    print(f"⏱️  Check Interval: {CHECK_INTERVAL_SECONDS} seconds")
    print(f"🔁 Max Retries:     {MAX_RETRIES} attempts")
    print(f"⏳ Retry Delay:     {RETRY_DELAY_SECONDS} seconds")
    print("Press [bold red]Ctrl+C[/bold red] at any time to stop the monitor.\n")

    notified_events: set[str] = set()
    current_token: str | None = None

    while True:
        cycle_start = time.time()
        try:
            current_token = check_away_matches(
                token=current_token,
                notified_events=notified_events,
                max_retries=MAX_RETRIES,
                retry_delay=RETRY_DELAY_SECONDS,
            )
        except KeyboardInterrupt:
            print("\n[yellow]Monitor stopped by user (Ctrl+C). Goodbye![/yellow]")
            break
        except Exception as e:
            print(f"[red]❌ Unexpected error in monitoring cycle: {e}[/red]")
            # Invalidate token so next cycle re-fetches a fresh one
            current_token = None

        # Calculate remaining time to sleep for the exact interval
        elapsed = time.time() - cycle_start
        sleep_time = max(0.0, CHECK_INTERVAL_SECONDS - elapsed)

        print(f"[dim]Waiting {sleep_time:.1f}s until next check...[/dim]")

        try:
            time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("\n[yellow]Monitor stopped by user (Ctrl+C). Goodbye![/yellow]")
            break


if __name__ == "__main__":
    main()
