import logging
from aiogram import Router, types, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.deep_linking import create_start_link
from config import N8N_FAMILY_URL
from http_client import http_client

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start_deep_link(message: types.Message, command: CommandObject):
    """Обробка Deep Link (наприклад, t.me/bot?start=join_123)"""
    args = command.args
    if args.startswith("join_"):
        invite_code = args.replace("join_", "")
        wait_msg = await message.answer("🔄 Обробка запрошення...")

        try:
            session = http_client.get_session()
            payload = {
                "action": "join_family",
                "chat_id": str(message.chat.id),
                "invite_code": invite_code
            }
            async with session.post(N8N_FAMILY_URL, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await wait_msg.edit_text(data.get("message", "Готово"))
                else:
                    await wait_msg.edit_text("❌ Помилка сервера при спробі приєднатися.")
        except Exception as e:
            logging.error(f"Join error: {e}")
            await wait_msg.edit_text("❌ Помилка з'єднання.")


@router.message(Command("family"))
async def cmd_family(message: types.Message):
    wait_msg = await message.answer("🔍 Шукаю інформацію...")
    try:
        session = http_client.get_session()
        payload = {"action": "get_info", "chat_id": str(message.chat.id)}
        async with session.post(N8N_FAMILY_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                # Прибрали Markdown, щоб уникнути помилок парсингу
                await wait_msg.edit_text(data.get("message", "Інфо не знайдено"))
            else:
                await wait_msg.edit_text("⚠️ Не вдалося отримати дані.")
    except Exception as e:
        logging.error(e)
        await wait_msg.edit_text("❌ Помилка.")


@router.message(Command("invite"))
async def cmd_invite(message: types.Message, bot: Bot):
    wait_msg = await message.answer("🎟 Генерую посилання...")
    try:
        session = http_client.get_session()
        payload = {"action": "create_invite", "chat_id": str(message.chat.id)}
        async with session.post(N8N_FAMILY_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                code = data.get("invite_code")
                if code:
                    bot_user = await bot.get_me()
                    link = f"https://t.me/{bot_user.username}?start=join_{code}"
                    await wait_msg.edit_text(
                        f"📩 **Запрошення готове!**\n\n"
                        f"Надішліть це посилання учаснику:\n`{link}`\n\n"
                        f"⚠️ Дійсне 24 години.",
                        parse_mode="Markdown"
                    )
                else:
                    await wait_msg.edit_text("❌ Не вдалося отримати код.")
            else:
                await wait_msg.edit_text("⚠️ Помилка сервера.")
    except Exception as e:
        logging.error(e)
        await wait_msg.edit_text("❌ Помилка.")


@router.message(Command("leave"))
async def cmd_leave(message: types.Message):
    await message.answer("⚠️ Ця дія створить для вас нову сім'ю. Ви впевнені? /confirm_leave")


@router.message(Command("confirm_leave"))
async def cmd_confirm_leave(message: types.Message):
    wait_msg = await message.answer("🚪 Виходимо...")
    try:
        session = http_client.get_session()
        payload = {
            "action": "leave_family",
            "chat_id": str(message.chat.id),
            "user_name": message.from_user.first_name or "User"
        }
        async with session.post(N8N_FAMILY_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                await wait_msg.edit_text(data.get("message", "Ви вийшли."))
            else:
                await wait_msg.edit_text("⚠️ Помилка.")
    except Exception as e:
        logging.error(e)
        await wait_msg.edit_text("❌ Помилка.")