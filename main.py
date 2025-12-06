import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
import aiohttp
from dotenv import load_dotenv

# Завантаження налаштувань
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
N8N_URL = os.getenv("N8N_WEBHOOK_URL")

# Налаштування
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


# --- КОМАНДИ МЕНЮ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привіт! Я бот для обліку фінансів.\n\n"
        "📸 Просто надішли мені фото чеку або натисни /scan.\n"
        "📊 Статистика: /stat"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "💡 **Як користуватися:**\n"
        "1. Зробіть фото чеку.\n"
        "2. Надішліть фото в цей чат.\n"
        "3. Я розпізнаю товари та запишу їх у таблицю.\n"
    )


@dp.message(Command("stat"))
async def cmd_stat(message: types.Message):
    # Тут поки заглушка. Пізніше ми зробимо запит до n8n, щоб він почитав Google Sheets
    await message.answer("🚧 Статистика поки в розробці. Скоро тут будуть твої витрати!")


@dp.message(Command("scan"))
async def cmd_scan(message: types.Message):
    await message.answer("📸 Чекаю на фото твого чеку. Просто скинь його сюди.")


# --- ОБРОБКА ФОТО ---

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    status_msg = await message.answer("⏳ Отримую фото та відправляю на аналіз...")

    try:
        # 1. Завантажуємо файл з серверів Telegram у пам'ять
        photo_id = message.photo[-1].file_id
        file = await bot.get_file(photo_id)
        file_content = await bot.download_file(file.file_path)

        # 2. Формуємо запит до n8n
        # Ми передаємо файл у полі 'data', щоб n8n одразу його підхопив
        form_data = aiohttp.FormData()
        form_data.add_field('data', file_content, filename='receipt.jpg')
        form_data.add_field('chat_id', str(message.chat.id))  # Передаємо ID користувача про всяк випадок

        # 3. Відправляємо
        # Створюємо конектор, який ігнорує SSL перевірку
        connector = aiohttp.TCPConnector(ssl=False)

        async with aiohttp.ClientSession(connector=connector) as session:  # <--- ЗМІНА ТУТ
            async with session.post(N8N_URL, data=form_data) as response:

                if response.status == 200:
                    # Якщо n8n надіслав JSON або текст у відповідь
                    server_response = await response.text()

                    # Тут можна красиво відформатувати відповідь, якщо n8n повертає JSON
                    # Поки виводимо як є
                    await status_msg.edit_text(f"✅ Чек успішно збережено!\n\nВідповідь сервера:\n{server_response}")
                else:
                    await status_msg.edit_text(f"❌ Помилка сервера n8n. Код: {response.status}")

    except Exception as e:
        logging.error(e)
        await status_msg.edit_text(f"❌ Щось пішло не так: {e}")


# --- ЗАПУСК ---
async def main():
    print("🚀 Бот запущено локально!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
