import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
import aiohttp
from dotenv import load_dotenv

# Завантаження налаштувань
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
N8N_SCAN_URL = os.getenv("N8N_WEBHOOK_URL")
N8N_STAT_URL = os.getenv("N8N_STAT_URL")

# Налаштування логування
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Глобальна змінна для HTTP сесії
http_session = None


# --- ЖИТТЄВИЙ ЦИКЛ БОТА ---

async def on_startup(dispatcher):
    """Створюємо сесію один раз при запуску бота"""
    global http_session
    connector = aiohttp.TCPConnector(ssl=False)
    http_session = aiohttp.ClientSession(connector=connector)
    logging.info("🚀 Бот запущено! HTTP сесія створена.")


async def on_shutdown(dispatcher):
    """Закриваємо сесію при зупинці"""
    global http_session
    if http_session:
        await http_session.close()
        logging.info("👋 HTTP сесія закрита.")


# Реєструємо функції
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


# --- КОМАНДИ МЕНЮ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привіт! Я ScanFlow бот.\n\n"
        "📸 Надішли фото чеку для обробки.\n"
        "📊 Натисни /stat щоб побачити витрати за місяць."
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "💡 **Як користуватися:**\n"
        "1. Зробіть фото чеку.\n"
        "2. Надішліть фото сюди -> я збережу витрати.\n"
        "3. Натисніть /stat -> я покажу діаграму витрат."
    )


@dp.message(Command("stat"))
async def cmd_stat(message: types.Message):
    """Отримання статистики з n8n"""
    wait_msg = await message.answer("📊 Рахую твої витрати...")

    if not N8N_STAT_URL:
        await wait_msg.edit_text("⚠️ Помилка налаштування: N8N_STAT_URL не знайдено.")
        return

    try:
        # Використовуємо глобальну сесію
        async with http_session.get(N8N_STAT_URL, params={"chat_id": message.chat.id}) as resp:
            if resp.status == 200:
                data = await resp.json()
                report_text = data.get("text_report", "Пусто")
                chart_url = data.get("image_url")

                # Якщо є графік - відправляємо фото, якщо ні - тільки текст
                if chart_url:
                    await message.answer_photo(photo=chart_url, caption=report_text)
                else:
                    await message.answer(report_text)

                # Видаляємо повідомлення "Рахую..."
                await wait_msg.delete()
            else:
                await wait_msg.edit_text(f"⚠️ n8n повернув помилку: {resp.status}")

    except Exception as e:
        logging.error(f"Stat error: {e}")
        await wait_msg.edit_text("❌ Не вдалося отримати статистику. Спробуйте пізніше.")


# --- ОБРОБКА ФОТО (ЧЕКІВ) ---

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    status_msg = await message.answer("⏳ Аналізую чек...")

    try:
        photo_id = message.photo[-1].file_id
        file = await bot.get_file(photo_id)
        file_content = await bot.download_file(file.file_path)

        form_data = aiohttp.FormData()
        form_data.add_field('data', file_content, filename='receipt.jpg')
        form_data.add_field('chat_id', str(message.chat.id))

        # Використовуємо глобальну сесію
        async with http_session.post(N8N_SCAN_URL, data=form_data) as response:
            if response.status == 200:
                # Читаємо те, що відповів n8n у вузлі "Respond to Webhook"
                server_text = await response.text()

                # Якщо n8n повернув порожній текст, показуємо заглушку, інакше - текст від n8n
                if not server_text.strip():
                    await status_msg.edit_text("✅ Чек прийнято! Обробка триває...")
                else:
                    await status_msg.edit_text(server_text)
            else:
                await status_msg.edit_text(f"❌ Помилка сервера n8n. Код: {response.status}")

    except Exception as e:
        logging.error(e)
        await status_msg.edit_text(f"❌ Помилка: {e}")


# --- ЗАПУСК ---
async def main():
    # Запускаємо полінг
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())