from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from collections import defaultdict
import logging

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
API_TOKEN = '7612235631:AAFkXSWsf7OcXZcKseZWDYhnImcWosrASaI'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Хранилище данных
user_stats = defaultdict(lambda: {"messages": 0, "photos": 0, "videos": 0, "links": 0, "audios": 0, "voice": 0, "video_notes": 0})

# Команда /all
@dp.message_handler(commands=['all'])
async def mention_all(message: types.Message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        await message.reply("Эта команда работает только в группах.")
        return

    members = await bot.get_chat_administrators(message.chat.id)
    mentions = " ".join([f"@{member.user.username}" for member in members if member.user.username])
    text = message.text.replace('/all', '').strip()
    await message.reply(f"{mentions}\n{text}")

# Кнопка "info"
@dp.message_handler(commands=['info'])
async def send_info(message: types.Message):
    user_id = message.from_user.id
    stats = user_stats[user_id]
    info_text = (
        f"Статистика для {message.from_user.full_name}:\n"
        f"Сообщений: {stats['messages']}\n"
        f"Фото: {stats['photos']}\n"
        f"Видео: {stats['videos']}\n"
        f"Ссылки: {stats['links']}\n"
        f"Аудио: {stats['audios']}\n"
        f"Голосовые сообщения: {stats['voice']}\n"
        f"Видеосообщения: {stats['video_notes']}"
    )
    await message.reply(info_text)

# Команда /top
@dp.message_handler(commands=['top'])
async def send_top(message: types.Message):
    sorted_users = sorted(user_stats.items(), key=lambda x: x[1]['messages'], reverse=True)
    top_text = "Топ участников по количеству сообщений:\n"
    for i, (user_id, stats) in enumerate(sorted_users, start=1):
        user = await bot.get_chat_member(message.chat.id, user_id)
        top_text += f"{i}. {user.user.full_name}: {stats['messages']} сообщений\n"
    await message.reply(top_text)

# Обработка всех сообщений для статистики
@dp.message_handler(content_types=types.ContentType.ANY)
async def count_messages(message: types.Message):
    user_id = message.from_user.id
    user_stats[user_id]["messages"] += 1

    if message.content_type == 'photo':
        user_stats[user_id]["photos"] += 1
    elif message.content_type == 'video':
        user_stats[user_id]["videos"] += 1
    elif message.content_type == 'audio':
        user_stats[user_id]["audios"] += 1
    elif message.content_type == 'voice':
        user_stats[user_id]["voice"] += 1
    elif message.content_type == 'video_note':
        user_stats[user_id]["video_notes"] += 1
    elif message.entities:
        for entity in message.entities:
            if entity.type == 'url':
                user_stats[user_id]["links"] += 1

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)