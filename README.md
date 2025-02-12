This Python bot provides remote control and administration capabilities for Windows PCs. It is built using Aiogram for the Telegram bot functionality and PyAutoGUI for task automation, allowing users to remotely perform various operations on their system.

Main Features:
System Management:

shutdown — Shut down the PC.
reboot — Reboot the PC.
sleep — Put the PC to sleep.
wakeup — Wake the PC from sleep.
logout — Log out of the current session.
System Information:

system_info — Get system statistics (CPU usage, memory usage, uptime).
ip_address — Get the external IP address.
File Management:

list_files — List files in a directory.
screenshot — Take a screenshot and send it via Telegram.
play_sound — Play audio files from the PC.
Automation:

minimize — Minimize all windows.
cmd — Launch the command prompt.
move_cursor — Randomly move the cursor on the screen.
stop_cursor — Stop moving the cursor.
max_volume — Set the volume to maximum.
Networking:

network_computers — Find available computers on the local network.
Screen Recording:

show_video — Record a screen video and send it via Telegram.
Bot Authentication:

The bot is available only to authorized users, whose IDs are added to the AUTHORIZED_USERS list.
Technologies Used:
Python: Primary programming language.
Aiogram: Framework for creating Telegram bots.
PyAutoGUI: For GUI automation (mouse, keyboard).
Psutil: For system monitoring.
OpenCV: For screen recording.
PyCaw: For audio management (volume control).
Subprocess & OS: For executing system commands.

Notes:
Works only on Windows.
Requires administrator rights to execute some commands.
The bot provides both a command-line interface and GUI automation, making it a versatile tool for remote control.
Disclaimer:
Use this bot with caution. Unauthorized use may affect system operation, including shutting down or rebooting the PC.
