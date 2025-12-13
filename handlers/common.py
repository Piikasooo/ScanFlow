from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привіт! Я ScanFlow бот v0.2.1\n\n"
        "📸 **Чек:** Надішли фото.\n"
        "📊 **Статистика:** /stat\n"
        "👨‍👩‍👧 **Сім'я:** /family\n"
        "🛍 **Каталоги:** Скоро..."
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "💡 **Довідка:**\n"
        "/stat - Ваші витрати\n"
        "/family - Хто у вашому бюджеті\n"
        "/invite - Запросити когось\n"
        "/leave - Вийти з сім'ї"
    )