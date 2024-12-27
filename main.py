from telethon import TelegramClient, events
import os
from datetime import datetime
from utils import sandjob

api_hash = sandjob.hash
api_id = sandjob.api
id_tg = sandjob.id

allowed_chats = [
    #123456789,
]
me = id_tg
print(f"ID client: {me}")

# Создаем директорию для логов и загрузок
os.makedirs(f"data/{id_tg}", exist_ok=True)
os.makedirs(f"data/{id_tg}/private", exist_ok=True)
os.makedirs(f"data/{id_tg}/groups", exist_ok=True)
os.makedirs(f"data/{id_tg}/channels", exist_ok=True)

# Инициализация клиента
#client = TelegramClient(tg_id, api_id, api_hash)

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
    with open(f"data/{id_tg}/genlog.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

async def list_chats():
    async for dialog in client.iter_dialogs():
        print(f"{dialog.name}: {dialog.id}")

#------------------------------------------------------------------------------------------------------------------
# Обработчик новых сообщений
@client.on(events.NewMessage)
async def handle_new_message(event):
    
    msgSender = event.sender_id # Сохраняем ID отправителя
    msgText = event.message.text or "<Без текста>" # Текст сообщения
    msgChat = event.chat_id
    isGroup = event.is_group
    isChannel = event.is_channel
    isPrivate = event.is_private
    
    if isPrivate:
        dir = f"data/private"
        down = f"data/private/{msgChat}/"
        log = f"data/private/{msgChat}.log"

    elif isChannel:
        dir = f"data/channels"
        down = f"data/channels/{msgChat}/"
        log = f"data/channels/{msgChat}.log"

    elif isGroup:
        dir = f"data/groups"
        down = f"data/groups/{msgChat}/"
        log = f"data/groups/{msgChat}.log"


    print(f"""
        Private: {isPrivate}
        Group: {isGroup}
        Channel: {isChannel}
        Chat: {msgChat}
        Sender: {msgSender}
        My ID: {me}
        Directory: {dir}
        Log: {log}
        Downloads: {down}
    """)

    if event.media:  # Если сообщение содержит медиа
        file_path = await event.download_media(file=down)
        log_message(log, msgSender, msgText, file_path)
        log_general(msgChat, msgSender, msgText, file_path)
    else:  # Если это текстовое сообщение
        log_message(log, msgSender, msgText)
        log_general(msgChat, msgSender, msgText)

#------------------------------------------------------------------------------------------------------------------
# Запускаем клиент
with client:
    print("Запуск клиента...")
    client.loop.run_until_complete(list_chats())
    client.run_until_disconnected()