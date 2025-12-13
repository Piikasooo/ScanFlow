import logging
from aiogram import Router, types
from aiogram.filters import Command
from config import N8N_STAT_URL
from http_client import http_client

router = Router()


@router.message(Command("stat"))
async def cmd_stat(message: types.Message):
    """Отримання статистики з n8n"""
    wait_msg = await message.answer("📊 Рахую твої витрати...")

    if not N8N_STAT_URL:
        await wait_msg.edit_text("⚠️ Помилка налаштування: N8N_STAT_URL не знайдено в .env")
        return

    try:
        # Отримуємо спільну сесію
        session = http_client.get_session()

        # Робимо запит до n8n
        async with session.get(N8N_STAT_URL, params={"chat_id": message.chat.id}) as resp:
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