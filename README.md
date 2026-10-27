# 🎟️ Feyenoord Away Ticket Monitor

An automated ticket monitor for Feyenoord away matches (*Uitwedstrijden*). It continuously checks the official Feyenoord ticket shop every few seconds and sends an instant Telegram notification with direct purchase links the moment tickets become available to buy!

---

## 🌟 Features

- **⚡ Fast Automated Checking**: Automatically polls the ticket system at your desired interval (e.g., every 10 seconds).
- **📲 Instant Telegram Alerts**: Sends a notification to your phone or Telegram group with match details and a direct purchase link.
- **🛡️ Built-in Network Retry**: Automatically retries failed requests if there are temporary internet hiccups or server timeouts.
- **🚫 Spam Prevention**: Once an alert is sent for a match, it won't repeatedly spam your phone every 10 seconds while it remains available. If tickets sell out and drop again later, a new alert is triggered immediately.
- **🖱️ 1-Click Launch**: 
  - **Windows**: Double-click `run_monitor.bat`
  - **MacBook / macOS**: Double-click `run_monitor.command`

---

## 🚀 Quick Start Guide (For Non-Technical Users)

### Step 1: Open the Project Folder
Make sure you have downloaded or cloned this folder onto your computer.

### Step 2: Configure Your Settings (`.env`)
In the folder, you will find a file named `.env` (or copy `.env.example` and rename it to `.env`).

Open this file with any text editor (like **Notepad** on Windows or **TextEdit** on Mac):

```env
# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Monitoring Settings
# How often to check for tickets (in seconds)
CHECK_INTERVAL_SECONDS=10

# Retry Settings
# Maximum number of retry attempts if internet/API fails
MAX_RETRIES=3

# Seconds to wait between each retry attempt
RETRY_DELAY_SECONDS=2
```

#### How to get your Telegram Bot Token & Chat ID:
1. **Get a Bot Token**:
   - Open Telegram and search for `@BotFather`.
   - Start a chat and send `/newbot`.
   - Follow the instructions to choose a name and username for your bot.
   - Copy the API token provided (looks like `7977711131:AAF40Sl...`) and paste it into `TELEGRAM_BOT_TOKEN`.
2. **Start Your Bot**:
   - Search for your newly created bot in Telegram and click **Start** (or send `/start`).
3. **Get Your Chat ID**:
   - In Telegram, search for `@userinfobot`.
   - Send any message to it; it will reply with your `Id` (a number like `1678140260`).
   - Copy this number and paste it into `TELEGRAM_CHAT_ID`.
4. **Save the File**:
   - Press <kbd>Ctrl + S</kbd> (Windows) or <kbd>Cmd + S</kbd> (Mac) to save.

---

## 💻 How to Run the Monitor

### 🪟 If You Are on Windows:

#### Method 1: Double-Click (Easiest)
1. Double-click the file named **`run_monitor.bat`**.
2. A command prompt window will open showing real-time updates.

#### Method 2: Via Terminal
Open PowerShell or Command Prompt in this folder and run:
```powershell
uv run main.py
```
*(or with standard Python):*
```powershell
python main.py
```

---

### 🍎 If You Are on a MacBook (macOS):

#### Method 1: Double-Click (Easiest)
1. Double-click the file named **`run_monitor.command`**.
2. A Mac Terminal window will launch and begin monitoring immediately.

> [!NOTE]
> **First-Time Mac Permission (if macOS says "cannot be opened because it is from an unidentified developer" or "permission denied")**:
> 1. Open Terminal (press <kbd>Cmd</kbd> + <kbd>Space</kbd>, type `Terminal`, and hit Enter).
> 2. Type `chmod +x ` (with a space at the end).
> 3. Drag and drop the `run_monitor.command` file from Finder directly into the Terminal window and press <kbd>Enter</kbd>.
> 4. Now you can double-click `run_monitor.command` anytime!

#### Method 2: Via Mac Terminal
Open Terminal in this folder and run:
```bash
uv run main.py
```
*(or with standard Python):*
```bash
python3 main.py
```

---

## 🛑 How to Stop the Monitor

- Press **`Ctrl + C`** in the open terminal window, or simply close the window.

---

## ⚙️ Configuration Reference

| Setting | Default | Description |
| :--- | :--- | :--- |
| `CHECK_INTERVAL_SECONDS` | `10` | The number of seconds between ticket checks (e.g. `10` = checks every 10 seconds). |
| `MAX_RETRIES` | `3` | If a network or server request drops, the script will retry this many times before moving to the next cycle. |
| `RETRY_DELAY_SECONDS` | `2` | Number of seconds to pause between retry attempts. |
| `TELEGRAM_BOT_TOKEN` | — | Your unique Telegram Bot Token from @BotFather. |
| `TELEGRAM_CHAT_ID` | — | Your personal Telegram user ID or group chat ID. |

---

## ❓ Frequently Asked Questions & Troubleshooting

### 1. I don't see any Telegram messages arriving!
- Make sure you opened a chat with your bot and clicked **Start** (or sent `/start`). Telegram bots cannot message you first until you initiate the conversation.
- Double-check that your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env` are exact and have no accidental spaces.

### 2. Why does the terminal say `Alert already sent previously`?
- This is an intentional feature! To protect you from receiving hundreds of notifications every minute, the bot only notifies you **once** when a match becomes available. It will notify you again if tickets sell out and later become available again.

### 3. How do I change how often it checks?
- Open `.env` in any text editor and change `CHECK_INTERVAL_SECONDS=10` to any number of seconds you want (e.g., `5` for 5 seconds, `30` for 30 seconds). Save the file and restart the monitor.

### 4. MacBook: Python is not recognized?
- If your Mac does not have Python installed yet, you can install it in seconds from [python.org](https://www.python.org/downloads/) or via Homebrew (`brew install python uv`).

---

## 🔒 Security Note
Never share or upload your `.env` file or your `TELEGRAM_BOT_TOKEN` to public websites (like GitHub). It contains private access credentials to your bot.
