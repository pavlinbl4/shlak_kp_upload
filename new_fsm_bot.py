"""
Начну создавать бота заново
"""

import asyncio
from collections import defaultdict

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from get_credentials import Credentials
from kp_photo_uploader_bot.common.bot_commands_list import kp_uploader
from loguru import logger

TOKEN = Credentials().pavlinbl4_bot
ALLOWED_USER_NAMES = {"PavlenkoEV", "anna44max"}

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
logger.info("Bot started to work")

"""Функция проверки допустимых типов отправленных файлов"""


def is_allowed_file_type(mime_type: str) -> bool:
    allowed_files_type = {'image/jpeg', 'image/png', 'image/x-tiff'}
    return mime_type in allowed_files_type


class FSMFillForm(StatesGroup):
    add_file = State()  # Состояние ожидания добавления файла
    add_credit = State()  # Состояние ожидания ввода image credit


"""handler_01 будет срабатывать на команду /start вне состояний"""


@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='Этот бот помогает добавлять фото в архив\n\n'
             'Чтобы перейти к отправке фото - '
             'отправьте команду /add_image'
    )
    logger.info("«Start» command set. handler_01")


"""handler_02 будет срабатывать на команду /help вне состояний"""


@dp.message(Command(commands='help'), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(
        text='Этот бот помогает добавлять фото в архив\n\n'
             'Чтобы перейти к отправке фото\n'
             'отправьте команду /add_image\n'
             f'без указания автора фото бот работать не будет!!!'
    )
    logger.info("«Help» command set. handler_02")


"""handler_03 будет срабатывать на команду /cancel вне состояний"""


@dp.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы прервали работу\n\n'
             'Чтобы вернуться к загрузке фото\n '
             'отправьте команду\n/add_image'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()
    logger.info("Send command «cancel». handler_03")


"""handler_04 будет срабатывать на команду /add_image вне состояний"""


@dp.message(Command(commands='add_image'), StateFilter(default_state), F.from_user.username.in_(ALLOWED_USER_NAMES))
async def process_add_image_command(message: Message, state: FSMContext):
    await message.answer(text='Сначала нужно указать автора/правообладателя снимка')
    # Устанавливаем состояние ожидания ввода имени автора
    await state.set_state(FSMFillForm.add_credit)
    logger.info("Send command «add_image» handler_03")


"""handler_05 будет срабатывать, если введено корректное имя (больше 3 букв)
и переходит в состояние ожидания файла"""


@dp.message(StateFilter(FSMFillForm.add_credit), F.text.len() > 3)
async def process_name_sent(message: Message, state: FSMContext):
    # сохраняем введенное имя в хранилище по ключу "credit"
    await state.update_data(credit=message.text)
    logger.info("Received credit from user handler_05")

    data = await state.get_data()
    logger.info(f"Received credit - {data['credit']} from user in handler_05")

    await message.answer(text=f"Credit : {data['credit']}\nОтправьте фото «как файл»,\nчтоб сохранить качество"
                              f"снимка")
    await state.set_state(FSMFillForm.add_file)
    logger.info("Wait file from user handler_05")


"""handler_06 будет срабатывать, если отправлен файл.
Проверяет, что снимок отправлен «как фото»
и переходит в состояние ожидания файла"""


@dp.message(StateFilter(FSMFillForm.add_file))
async def handle_allowed_user_messages(message: types.Message, state: FSMContext):
    logger.info("Handler_06")
    try:
        logger.info(f'{message.document.mime_type = }')
        logger.info(f'{message.photo = }')
        logger.info(f'{message.media_group_id = }')
    except AttributeError as ex:
        logger.info(f'{ex = }')
        logger.info(f'{message.photo = }')


    # если message.document is None - значит прислали не файл и не группу файлов

    if message.document is None and message.media_group_id is None:
        logger.info("No media_group and No document")
        await message.answer(f"Отправьте фото «как файл», чтоб сохранить качество\n"
                             f"снимка")
        await state.set_state(FSMFillForm.add_file)

    # прислана группа фотографий как альбом
    elif message.media_group_id and message.photo:
        logger.info("Photos in album")
        await message.answer(f"Отправьте фото «как файл», чтоб сохранить качество\n"
                             f"снимка")
        await state.set_state(FSMFillForm.add_file)

    # Проверяем, является ли сообщение частью медиа группы и в ней присланы файлы
    elif message.media_group_id and message.photo is None:
        # Временное хранилище для медиа группа
        media_groups = defaultdict(list)
        logger.info("Send media_group")

        async def process_group_after_timeout(media_group_id: str):
            """Ожидает 2 секунды и обрабатывает группу."""
            await asyncio.sleep(2)  # Ждем 2 секунды

        # Добавляем сообщение в группу
        media_groups[message.media_group_id].append(message)
        # Запускаем таймер для обработки группы
        asyncio.create_task(process_group_after_timeout(message.media_group_id))

        # Проверяем, есть ли еще сообщения в группе
        if message.media_group_id in media_groups:
            group_messages = media_groups[message.media_group_id]
            logger.info("Process media-group")
            await message.answer(f"You send  file {message.document.file_name}")
            # await process_media_group(group_messages)  # Обрабатываем группу
            del media_groups[message.media_group_id]  # Удаляем группу из хранилища

        # Ждем 1 секунду, чтобы собрать все сообщения группы
        await asyncio.sleep(1)



    # проверяем что прислан файл
    elif message.document:
        # нужно проверить, что файл соответствующего типа  !!!
        logger.info("Single file")
        await message.answer(f"You send single file {message.document.file_name}")
        # check_file()
        # Обрабатываем одиночный файл
        # await process_single_file(message)


# start polling
if __name__ == '__main__':
    async def set_main_menu():
        await bot.set_my_commands(commands=kp_uploader)


    dp.startup.register(set_main_menu)
    dp.run_polling(bot)
