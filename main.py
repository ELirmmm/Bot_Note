import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault

from app.database.models import async_main
from app.handlers import router
from config import TOKEN

if not TOKEN:
    raise ValueError("Переменная TOKEN не найдена в файле .env!")

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(
            command="view_minds",
            description="Вывести все мысли с нумерацией (только при открытом файле)",
        ),
        BotCommand(
            command="view_notes",
            description="Вывести названия всех заметок с нумерацией",
        ),
        BotCommand(
            command="merge",
            description="Объединить содержимое двух заметок в одной",
        ),
        BotCommand(
            command="note",
            description="Показать конкретную мысль по её номеру (пример: note 3, только при открытом файле)",
        ),
        BotCommand(
            command="edit",
            description="Дополнить мысль новой строчкой (пример: edit 3, только при открытом файле)",
        ),
        BotCommand(
            command="delete_mind",
            description="Удалить мысль (пример: delete_mind 3, только при открытом файле)",
        ),
        BotCommand(
            command="delete_note",
            description="Удалить заметку (пример: delete_note имя_заметки)",
        ),
    ]
    await bot.set_my_commands(
        commands=main_menu_commands, scope=BotCommandScopeDefault()
    )


async def main():
    await async_main()
    dp.include_router(router=router)
    await set_main_menu(bot)
    await dp.start_polling(bot)  # type: ignore


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
