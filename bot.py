import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_data.config import Config, load_config
from handlers.user_handlers import register_user_handlers
from handlers.other_handlers import register_other_handlers
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Фнукция для регистрации всех хэндлеров
def register_all_handlers(dp: Dispatcher) -> None:
    register_user_handlers(dp)
    register_other_handlers(dp)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
    storage: MemoryStorage = MemoryStorage()

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher(bot, storage=storage)

    # Регистрируем все хэндлеры
    register_all_handlers(dp)

    # Запускаем polling
    try:
        await dp.skip_updates()
        await dp.start_polling()
    finally:
        await bot.close()


if __name__ == '__main__':
    try:
        # Запускаем функцию main
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Выводим в консоль сообщение об ошибке,
        # если получены исключения KeyboardInterrupt или SystemExit
        logger.error('Bot stopped!')