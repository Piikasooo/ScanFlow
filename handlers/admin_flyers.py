import logging
import traceback
from aiogram import Router, F, types, Bot
from aiogram.exceptions import TelegramBadRequest
from config import ADMIN_ID, N8N_FLYER_URL
from http_client import http_client

router = Router()


@router.message(F.document, F.from_user.id == ADMIN_ID)
async def handle_flyer_upload(message: types.Message, bot: Bot):
    doc = message.document

    # 1. Перевірка формату
    if "pdf" not in doc.mime_type and not doc.file_name.lower().endswith(".pdf"):
        await message.answer("⚠️ Це не PDF. Надішліть файл .pdf")
        return

    if not N8N_FLYER_URL:
        await message.answer("❌ Помилка: N8N_FLYER_URL не налаштовано.")
        return

    status_msg = await message.answer("⏳ **Отримано! Передаю на аналіз в AI...**")

    try:
        # 2. Отримуємо посилання на файл (якщо < 20MB)
        file_url = None
        try:
            file_info = await bot.get_file(doc.file_id)
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        except TelegramBadRequest:
            await status_msg.edit_text("⚠️ Файл великий (>20MB). AI спробує завантажити його за ID.")

        # 3. Відправка в n8n
        # Ми більше НЕ шлемо в канал тут. Це зробить n8n після обробки.
        payload = {
            "file_url": file_url,
            "telegram_file_id": str(doc.file_id),
            "telegram_unique_id": str(doc.file_unique_id),
            "file_name": doc.file_name,
            "chat_id": str(message.chat.id)
        }

        session = http_client.get_session()
        logging.info(f"Sending flyer to n8n...")

        async with session.post(N8N_FLYER_URL, json=payload) as response:
            if response.status == 200:
                # n8n відповість, що "Прийнято в роботу"
                # А результат прийде в канал пізніше
                await status_msg.edit_text(
                    "🚀 **Файл передано!**\nОчікуйте публікацію в каналі після розпізнавання (1-2 хв).")
            else:
                err_text = await response.text()
                await status_msg.edit_text(f"❌ Помилка n8n ({response.status}):\n{err_text[:200]}")

    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Flyer Error: {error_trace}")
        await status_msg.edit_text(f"❌ Помилка бота: {e}")