import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from http_client import http_client

# Імпортуємо наші модулі
from handlers import common, families, statistics, scanner, admin_flyers

# Налаштування логування
logging.basicConfig(level=logging.INFO)


async def on_startup(dispatcher):
    http_client.get_session()
    logging.info("🚀 Бот запущено! HTTP сесія створена.")


async def on_shutdown(dispatcher):
    await http_client.close()
    logging.info("👋 HTTP сесія закрита.")


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Реєструємо функції життєвого циклу
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # 🔄 ПІДКЛЮЧАЄМО РОУТЕРИ (Порядок важливий!)
    # 1. Адмінка (щоб ловити файли першою)
    dp.include_router(admin_flyers.router)

    # 2. Специфічні команди
    dp.include_router(families.router)
    dp.include_router(statistics.router)

    # 3. Загальні команди (/start, /help)
    dp.include_router(common.router)

    # 4. Сканер (ловить всі фото, тому в кінці)
    dp.include_router(scanner.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())