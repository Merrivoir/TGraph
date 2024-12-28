from telethon import TelegramClient, events
import os
import asyncio
from datetime import datetime
from utils import sandjob

api_hash = sandjob.hash
api_id = sandjob.api
name = sandjob.name

allowed_chats = [
    #123456789,
]

dialog_list = {}

genDir = f"data/{name}"
prvDir = f"data/{name}/private"
grpDir = f"data/{name}/groups"
cnlDir = f"data/{name}/channels"

os.makedirs(genDir, exist_ok=True)
os.makedirs(prvDir, exist_ok=True)
os.makedirs(grpDir, exist_ok=True)
os.makedirs(cnlDir, exist_ok=True)

# Инициализация клиента
client = TelegramClient(name, api_id, api_hash)

#------------------------------------------------------------------------------------------------------------------
# Функция для логирования сообщений

def log_message(log, sender, message, file_path=None):
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}]  {sender}: {message}\n"

    if file_path:  # Если есть медиафайл
        log_entry += f"Медиафайл: {file_path}\n"

    # Сохраняем лог в файл
    with open(log, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

def log_general(chat, sender, message, file_path=None):
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} | {chat} | {sender}: {message}\n"

    if file_path:  # Если есть медиафайл
        log_entry += f"Медиафайл: {file_path}\n"

    # Сохраняем лог в файл
    with open(f"{genDir}/general.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

def log_staff(message):
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp}\n{message}\n\n"

    # Сохраняем лог в файл
    with open(f"{genDir}/staff.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

#------------------------------------------------------------------------------------------------------------------
# Список чатов при запуске

async def chat_list():
    async for dialog in client.iter_dialogs():
        chat_name = dialog.title or dialog.name or "Личный чат"
        dialog_list[dialog.id] = chat_name
        print(f"{chat_name}: {dialog.id}")
    
    log_staff(dialog_list)

#------------------------------------------------------------------------------------------------------------------
# Обработчик новых сообщений

async def update_dialog_list():
    """Функция для обновления списка диалогов."""
    global dialog_list
    while True:
        async for dialog in client.iter_dialogs():
            if dialog.id not in dialog_list:
                chat_name = dialog.title or dialog.name or "Личный чат"
                dialog_list[dialog.id] = chat_name
                print(f"Новый диалог: {chat_name}")
                log_staff(f"Новый диалог: {chat_name}")
        await asyncio.sleep(10)  # Проверка каждые 10 секунд

#------------------------------------------------------------------------------------------------------------------
# Обработчик новых сообщений

async def listen_to_messages():
    @client.on(events.NewMessage)
    async def handle_new_message(event):
        msgSender = event.sender_id # Сохраняем ID отправителя
        msgText = event.message.text or "<Без текста>" # Текст сообщения
        msgChat = event.chat_id
        isGroup = event.is_group
        isChannel = event.is_channel
        isPrivate = event.is_private
        
        if isPrivate:
            dir = prvDir
            down = f"{prvDir}/{msgChat}/"
            log = f"{prvDir}/{msgChat}.log"

        elif isChannel:
            dir = cnlDir
            down = f"{cnlDir}/{msgChat}/"
            log = f"{cnlDir}/{msgChat}.log"

        elif isGroup:
            dir = grpDir
            down = f"{grpDir}/{msgChat}/"
            log = f"{grpDir}/{msgChat}.log"

        print(f"""Private: {isPrivate}
            Group: {isGroup}
            Channel: {isChannel}
            Chat: {msgChat}
            Sender: {msgSender}
            Directory: {dir}""")

        if event.media:  # Если сообщение содержит медиа
            file_path = await event.download_media(file=down)
            log_message(log, msgSender, msgText, file_path)
            log_general(msgChat, msgSender, msgText, file_path)
        else:  # Если это текстовое сообщение
            log_message(log, msgSender, msgText)
            log_general(msgChat, msgSender, msgText)
    
    await client.run_until_disconnected()

#------------------------------------------------------------------------------------------------------------------
# Запускаем клиент

async def main():
    await chat_list()
    """Запуск обеих функций параллельно."""
    await asyncio.gather(
        listen_to_messages(),
        update_dialog_list()
    )

# Запуск клиента
with client:
    client.loop.run_until_complete(main())