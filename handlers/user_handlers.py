import numpy as np
from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from lexicon.lexicon_ru import LEXICON_RU
from services.services import stylize_image
import cv2


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    fill_sample = State()  # Состояние ожидания ввода исходного изображения
    fill_style = State()  # Состояние ожидания ввода изображения стиля


# Этот хэндлер срабатывает на команду /start
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'])
    # Устанавливаем состояние ожидания ввода исходного изображения
    await FSMFillForm.fill_sample.set()


# Этот хендлер будет срабатывать, если во время отправки фото что-то пошло не так
async def warning_not_photo(message: Message):
    await message.answer(text=LEXICON_RU['not_image'])


# Этот хендлер будет срабатывать при отправке исходного изображения
async def process_sample_photo_sent(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['sample_photo_id'] = message.photo[-1].file_id

    await message.answer(text=LEXICON_RU['ask_style'])

    await FSMFillForm.fill_style.set()


# Этот хендлер будет срабатывать при отправке изображения стиля
async def process_style_photo_sent(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['style_photo_id'] = message.photo[-1].file_id

    # Собираем данные
    photos = await state.get_data()
    bot = message.bot

    # получаем изображения в байтах
    sample_img = await get_image_bytes(bot, photos['sample_photo_id'])
    style_img = await get_image_bytes(bot, photos['style_photo_id'])

    await state.finish()

    await message.answer(text=LEXICON_RU['need_to_wait'])

    await message.answer_photo(photo=stylize_image(sample_img, style_img))


# Функция для скачивания изображений из бота [НЕ ИСПОЛЬЗУЕТСЯ]
async def get_image(bot, photo):
    f = await bot.get_file(photo)
    f = await bot.download_file(f.file_path)
    f_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
    img = cv2.imdecode(f_bytes, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    return img


# Функция для скачивания байтового представления фото
async def get_image_bytes(bot, photo):
    f = await bot.get_file(photo)
    img = await bot.download_file(f.file_path)

    return img


# Этот хэндлер срабатывает на команду /help
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


# Функция для регистрации хэндлеров в диспетчере. Вызывается в исполняемом файле bot.py
def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(process_start_command, commands='start')
    dp.register_message_handler(process_help_command, commands='help')
    dp.register_message_handler(process_sample_photo_sent,
                                content_types='photo',
                                state=FSMFillForm.fill_sample)
    dp.register_message_handler(warning_not_photo,
                                content_types='any',
                                state=FSMFillForm.fill_sample)
    dp.register_message_handler(process_style_photo_sent,
                                content_types='photo',
                                state=FSMFillForm.fill_style)
    dp.register_message_handler(warning_not_photo,
                                content_types='any',
                                state=FSMFillForm.fill_style)
