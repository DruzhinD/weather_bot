from aiogram import Bot, Dispatcher
import asyncio

from chatbot.main_router import main_router
from common.config import Config


async def main():
    config = Config()
    bot = Bot(config.bot_token)

    dp = Dispatcher()
    dp.include_router(main_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())