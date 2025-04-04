🔧 Discord Remote Administration Bot

📌 Description

This is an advanced Discord-based remote administration tool, allowing users to interact with and control a system remotely via Discord commands. The bot supports system monitoring, process management, file transfers, and live data capture, making it useful for remote 

administration, automation, and security research.

🛠️ Features
✅ System Information: Fetch OS, CPU, RAM, Disk, GPU, and network details

✅ Shell Command Execution: Run terminal commands remotely

✅ Process Management: List, open, and terminate system processes

✅ File Handling: Upload and download files between the remote system and Discord

✅ Screen Capture: Take and send screenshots of the desktop

✅ Webcam Capture: Capture and send an image using the webcam

✅ Browser Data Extraction: Retrieve saved passwords and browsing history (Chrome)

✅ Keylogger: Monitor and log keystrokes in the background

✅ Microphone Streaming: Live audio capture and streaming to a Discord voice channel

✅ Clipboard Data Extraction: Retrieve copied text from the clipboard

✅ Hardware Monitoring: Track CPU, RAM, and GPU usage in real-time

✅ Network Scanner: Identify active devices on the local network


🚀 Setup & Installation

Install dependencies:

bash

Copier

Modifier

pip install discord pynput pyaudio psutil requests pycryptodome opencv-python GPUtil pillow

Configure the bot: Replace DISCORD_BOT_TOKEN with your bot's token.


Run the script:


bash

Copier

Modifier

python bot.py

Add the bot to your Discord server and give it the necessary permissions.


🔗 Usage
Interact with the bot using commands in a Discord server:

!sysinfo → Get detailed system info (OS, RAM, CPU, GPU, IP, etc.)

!cmd <command> → Execute a shell command and return the output

!screen → Take a screenshot and send it via Discord

!screen_cam → Capture an image from the webcam

!history → Extract Chrome browsing history

!grab_passwd → Retrieve saved passwords (Chrome)

!key_logger → Start keylogging and retrieve captured keystrokes

!mic_stream → Stream live microphone audio to a Discord voice channel

!process → List active processes

!kill_process <name> → Terminate a process

!open_process <name> → Start a process

!download <file_path> → Download a file from the target system

!upload <url> <save_path> → Download a file from a URL to the system

📌 Disclaimer
This project is for learning and ethical hacking purposes. Any unauthorized use is strictly prohibited. Be responsible!
