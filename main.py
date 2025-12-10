import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.deep_linking import create_start_link
import aiohttp
from dotenv import load_dotenv

# Завантаження налаштувань
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
N8N_SCAN_URL = os.getenv("N8N_WEBHOOK_URL")
N8N_STAT_URL = os.getenv("N8N_STAT_URL")
N8N_FAMILY_URL = os.getenv("N8N_FAMILY_URL")  # Новий URL для family manager

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


dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


# --- КОМАНДИ ---

@dp.message(CommandStart(deep_link=True))
async def cmd_start_deep_link(message: types.Message, command: CommandObject):
    """Обробка Deep Link (наприклад, t.me/bot?start=join_123)"""
    args = command.args

    if args.startswith("join_"):
        invite_code = args.replace("join_", "")
        wait_msg = await message.answer("🔄 Обробка запрошення...")

        try:
            payload = {
                "action": "join_family",
                "chat_id": str(message.chat.id),
                "invite_code": invite_code
            }
            async with http_session.post(N8N_FAMILY_URL, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await wait_msg.edit_text(data.get("message", "Готово"))
                else:
                    await wait_msg.edit_text("❌ Помилка сервера при спробі приєднатися.")
        except Exception as e:
            logging.error(e)
            await wait_msg.edit_text("❌ Помилка з'єднання.")
    else:
        await cmd_start(message)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Звичайний старт (реєстрація через ScanFlow відбудеться при першому чеку)"""
    await message.answer(
        "👋 Привіт! Я ScanFlow бот.\n\n"
        "📸 **Чек:** Просто надішли фото.\n"
        "📊 **Статистика:** /stat\n"
        "👨‍👩‍👧 **Сім'я:** /family (керування бюджетом)"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "💡 **Довідка:**\n"
        "/stat - Ваші витрати\n"
        "/family - Хто у вашому бюджеті\n"
        "/invite - Запросити когось у сім'ю\n"
        "/leave - Вийти та створити свій окремий бюджет"
    )


@dp.message(Command("family"))
async def cmd_family(message: types.Message):
    """Отримати інфо про сім'ю"""
    wait_msg = await message.answer("🔍 Шукаю інформацію...")
    try:
        payload = {"action": "get_info", "chat_id": str(message.chat.id)}
        async with http_session.post(N8N_FAMILY_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                # Markdown відповідь з n8n
                await wait_msg.edit_text(data.get("message", "Інфо не знайдено"))
            else:
                await wait_msg.edit_text("⚠️ Не вдалося отримати дані.")
    except Exception as e:
        logging.error(e)
        await wait_msg.edit_text("❌ Помилка.")


@dp.message(Command("invite"))
async def cmd_invite(message: types.Message):
    """Створити запрошення"""
    wait_msg = await message.answer("🎟 Генерую посилання...")
    try:
        payload = {"action": "create_invite", "chat_id": str(message.chat.id)}
        async with http_session.post(N8N_FAMILY_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                code = data.get("invite_code")
                if code:
                    # Генеруємо посилання засобами aiogram
                    bot_username = (await bot.get_me()).username
                    link = f"https://t.me/{bot_username}?start=join_{code}"

                    await wait_msg.edit_text(
                        f"📩 **Запрошення готове!**\n\n"
                        f"Надішліть це посилання людині, яку хочете додати до бюджету:\n`{link}`\n\n"
                        f"⚠️ Посилання дійсне 24 години.",
                        parse_mode="Markdown"
                    )
                else:
                    await wait_msg.edit_text("❌ Не вдалося отримати код.")
            else:
                await wait_msg.edit_text("⚠️ Помилка сервера.")
    except Exception as e:
        logging.error(e)
        await wait_msg.edit_text("❌ Помилка.")


@dp.message(Command("leave"))
async def cmd_leave(message: types.Message):
    """Вийти з сім'ї"""
    await message.answer("⚠️ Ця дія створить для вас нову, пусту сім'ю. Ви впевнені? /confirm_leave")


@dp.message(Command("confirm_leave"))
async def cmd_confirm_leave(message: types.Message):
    wait_msg = await message.answer("🚪 Виходимо...")
    try:
        payload = {
            "action": "leave_family",
            "chat_id": str(message.chat.id),
            "user_name": message.from_user.first_name or "User"
        }
        async with http_session.post(N8N_FAMILY_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                await wait_msg.edit_text(data.get("message", "Ви вийшли."))
            else:
                await wait_msg.edit_text("⚠️ Помилка.")
    except Exception as e:
        logging.error(e)
        await wait_msg.edit_text("❌ Помилка.")


# --- СТАТИСТИКА (без змін) ---
@dp.message(Command("stat"))
async def cmd_stat(message: types.Message):
    wait_msg = await message.answer("📊 Рахую твої витрати...")
    if not N8N_STAT_URL:
        await wait_msg.edit_text("⚠️ Налаштування N8N_STAT_URL відсутнє.")
        return

    try:
        async with http_session.get(N8N_STAT_URL, params={"chat_id": message.chat.id}) as resp:
            if resp.status == 200:
                data = await resp.json()
                report_text = data.get("text_report", "Пусто")
                chart_url = data.get("image_url")
                if chart_url:
                    await message.answer_photo(photo=chart_url, caption=report_text)
                else:
                    await message.answer(report_text)
                await wait_msg.delete()
            else:
                await wait_msg.edit_text(f"⚠️ n8n error: {resp.status}")
    except Exception as e:
        logging.error(f"Stat error: {e}")
        await wait_msg.edit_text("❌ Помилка статистики.")


# --- ОБРОБКА ФОТО (без змін, але з глобальною сесією) ---
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

        async with http_session.post(N8N_SCAN_URL, data=form_data) as response:
            if response.status == 200:
                server_text = await response.text()
                if not server_text.strip():
                    await status_msg.edit_text("✅ Чек прийнято!")
                else:
                    await status_msg.edit_text(server_text)
            else:
                await status_msg.edit_text(f"❌ Помилка n8n: {response.status}")
    except Exception as e:
        logging.error(e)
        await status_msg.edit_text(f"❌ Error: {e}")


# --- ЗАПУСК ---
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())