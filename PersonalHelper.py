from telethon import TelegramClient, events
import openai
import os
from pydub import AudioSegment  # Для конвертации аудио
import speech_recognition as sr  # Для распознавания речи

# Настройки
api_id = os.getenv("TONE")  # Ваш API ID
api_hash = os.getenv("TTWO")  # Ваш API Hash
openai.api_key = os.getenv("oai_key")  # Ваш ключ OpenAI

# Идентификатор пользователя
TARGET_USER_ID = 1912365148

# Инициализация клиента Telegram
client = TelegramClient('ai_chat', api_id, api_hash)

# Хранилище контекста
chat_context = []

# Директория для сохранения файлов
FILE_DIRECTORY = "files"
os.makedirs(FILE_DIRECTORY, exist_ok=True)

def generate_ai_response(user_message):
    global chat_context

    # Добавляем сообщение пользователя в контекст
    chat_context.append({"role": "user", "content": user_message})

    try:
        # Отладочная информация
        print("Отправляемый контекст:", chat_context)

        # Запрос к OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                *chat_context
            ]
        )
        
        # Извлекаем ответ AI
        ai_reply = response.choices[0].message["content"].strip()
        chat_context.append({"role": "assistant", "content": ai_reply})

        # Ограничиваем длину контекста
        if len(chat_context) > 20:
            chat_context = chat_context[-20:]

        return ai_reply

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return "Произошла непредвиденная ошибка."

# Функция обработки аудио
def transcribe_audio(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        audio.export(file_path + ".wav", format="wav")  # Конвертация в WAV

        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path + ".wav") as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            return text
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return "Не удалось распознать голосовое сообщение."

# Обработка сообщений
@client.on(events.NewMessage)
async def handle_new_message(event):
    sender = await event.get_sender()
    sender_id = sender.id

    if sender_id == TARGET_USER_ID:
        if event.message.message:
            user_message = event.message.message
            print(f"Сообщение от пользователя: {user_message}")

            ai_response = generate_ai_response(user_message)
            print(f"Ответ ИИ: {ai_response}")
            await client.send_message(TARGET_USER_ID, ai_response)

        # Обработка вложений
        if event.message.media:
            file_path = await event.download_media(file=FILE_DIRECTORY)
            print(f"Получен файл: {file_path}")

            if event.message.file.mime_type.startswith("image"):
                # Если это изображение
                await client.send_message(TARGET_USER_ID, "Я получил изображение. Чем могу помочь?")
            elif event.message.file.mime_type.startswith("audio"):
                # Если это голосовое сообщение
                transcription = transcribe_audio(file_path)
                print(f"Транскрипция: {transcription}")
                await client.send_message(TARGET_USER_ID, f"Я расшифровал голосовое сообщение:\n{transcription}")
            else:
                await client.send_message(TARGET_USER_ID, "Я получил вложение. Обработка пока не поддерживается.")

# Запуск клиента
with client:
    print("Бот запущен и слушает сообщения...")
    client.run_until_disconnected()
