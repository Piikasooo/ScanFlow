import logging
import aiohttp
from aiogram import Router, F, types, Bot
from config import N8N_SCAN_URL
from http_client import http_client

router = Router()


@router.message(F.photo)
async def handle_photo(message: types.Message, bot: Bot):
    """
    Обробка фото чеків.
    bot: Bot передається автоматично aiogram-ом завдяки dependency injection
    """
    status_msg = await message.answer("⏳ Аналізую чек...")

    try:
        # Отримуємо файл з Telegram (беремо найбільший розмір -1)
        photo_id = message.photo[-1].file_id
        file = await bot.get_file(photo_id)

        # Завантажуємо байт-код файлу
        file_content = await bot.download_file(file.file_path)

        # Формуємо multipart-запит для n8n
        form_data = aiohttp.FormData()
        form_data.add_field('data', file_content, filename='receipt.jpg')
        form_data.add_field('chat_id', str(message.chat.id))

        # Використовуємо спільну сесію
        session = http_client.get_session()

        async with session.post(N8N_SCAN_URL, data=form_data) as response:
            if response.status == 200:
                # Читаємо відповідь від n8n (Respond to Webhook)
                server_text = await response.text()

                if not server_text.strip():
                    await status_msg.edit_text("✅ Чек прийнято! Обробка триває...")
                else:
                    await status_msg.edit_text(server_text)
            else:
                await status_msg.edit_text(f"❌ Помилка сервера n8n. Код: {response.status}")

    except Exception as e:
        logging.error(f"Scanner Error: {e}")
        await status_msg.edit_text(f"❌ Помилка обробки: {e}")