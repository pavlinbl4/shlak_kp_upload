from pathlib import Path
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

from kp_photo_uploader_bot.check_existing_file import create_dir
from kp_photo_uploader_bot.image_converter.convert_images import convert_image_to_jpeg
from photo_uplolader.shlack_uploader import web_photo_uploader

TOKEN = Credentials().pavlinbl4_bot
ALLOWED_USER_NAMES = {"PavlenkoEV", "anna44max"}

storage = MemoryStorage()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
logger.info("Bot started to work")

def is_allowed_file_type(mime_type: str) -> bool:
    allowed_files_type = {'image/jpeg', 'image/png', 'image/x-tiff'}
    logger.info(f'{mime_type in allowed_files_type = }')
    return mime_type in allowed_files_type

def convert_to_jpeg_if_needed(file_path: str) -> str:
    if Path(file_path).suffix.lower() not in ['.jpeg', '.jpg']:
        return convert_image_to_jpeg(file_path)
    return file_path

async def save_file_to_disk(file_path: str, destination_path: str) -> None:
    await bot.download_file(file_path, destination_path)

async def selenium_photo_uploader(message, state):
    data = await state.get_data()
    await message.answer(text='Спасибо!\n\nВ ближайшее время вам поступит id снимка')
    logger.info(f"{data = }")
    photo_id = web_photo_uploader(data["path_to_uploaded_image"], message.document.file_name, data["credit"])
    logger.info(f"{photo_id = }")
    await message.answer(text=f'Готово!\n\n{photo_id = }')

async def process_single_file(message: types.Message, state: FSMContext) -> None:
    if not is_allowed_file_type(message.document.mime_type):
        await message.answer(f"Вы отправили недопустимый тип файла\n"
                             f"{message.document.mime_type}\n"
                             f"я работаю только с фотографиями")
        await state.set_state(FSMFillForm.add_file)
    else:
        try:
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            logger.info(f'{file_id = }')

            uploaded_images = create_dir("Uploaded_images")
            path_to_uploaded_image = f"{uploaded_images}/{message.document.file_name}"
            logger.info(f"{path_to_uploaded_image = }")

            await save_file_to_disk(file_path, path_to_uploaded_image)

            path_to_uploaded_image = convert_to_jpeg_if_needed(path_to_uploaded_image)
            await state.update_data(path_to_uploaded_image=path_to_uploaded_image)

            await message.answer(f"{hbold(message.from_user.full_name)}\n"
                                 f"вы загрузили файл\n{hbold(message.document.file_name)}\n"
                                )
            await selenium_photo_uploader(message, state)

        except Exception as e:
            logger.error(f"Error processing file {message.document.file_name}: {e}")
            await message.answer(
                f"Произошла ошибка при обработке файла {message.document.file_name}. Пожалуйста, попробуйте еще раз.")

class FSMFillForm(StatesGroup):
    add_file = State()
    add_credit = State()

@dp.message(CommandStart())
async def process_start_command(message: Message, ):
    await message.answer(
        text='Этот бот помогает добавлять фото в архив\n\n'
             'Чтобы перейти к отправке фото - '
             'отправьте команду /add_image'
    )
    logger.info("«Start» command set handler_01 wait for add_credit")

@dp.message(Command(commands='help'), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(
        text='Этот бот помогает добавлять фото в архив\n\n'
             'Чтобы перейти к отправке фото\n'
             'отправьте команду /add_image\n'
             f'без указания автора фото бот работать не будет!!!'
    )
    logger.info("«Help» command set. handler_02")

@dp.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы прервали работу\n\n'
             'Чтобы вернуться к загрузке фото\n '
             'отправьте команду\n/add_image'
    )
    await state.clear()
    logger.info("Send command «cancel». handler_03")

@dp.message(Command(commands='add_image'), StateFilter(default_state), F.from_user.username.in_(ALLOWED_USER_NAMES))
async def process_add_image_command(message: Message, state: FSMContext):
    await message.answer(text='Сначала нужно указать автора/правообладателя снимка')
    await state.set_state(FSMFillForm.add_credit)
    logger.info("Send command «add_image» handler_04")

@dp.message(StateFilter(FSMFillForm.add_credit), F.text.len() > 3)
async def process_name_sent(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(credit=message.text)
        logger.info("Received credit from user handler_05")

        data = await state.get_data()
        logger.info(f"Received credit - {data['credit']} from user in handler_05")

        await message.answer(text=f"Credit : {data['credit']}\nОтправьте фото «как файл»,\nчтоб сохранить качество"
                                  f"снимка")
        await state.set_state(FSMFillForm.add_file)
        logger.info("Wait file from user handler_05")
    else:
        await message.answer(text=f"Сначала нужно указать автора")
        await state.set_state(FSMFillForm.add_credit)

@dp.message(StateFilter(FSMFillForm.add_file))
async def handle_allowed_user_messages(message: types.Message, state: FSMContext):
    logger.info("Handler_06")

    if message.document is None and message.media_group_id is None:
        logger.info("No media_group and No document")
        await message.answer(f"Отправьте фото «как файл», чтоб сохранить качество\n"
                             f"снимка")
        await state.set_state(FSMFillForm.add_file)

    elif message.media_group_id and message.photo:
        logger.info("Photos in album")
        await message.answer(f"Отправьте фото «как файл», чтоб сохранить качество\n"
                             f"снимка")
        await state.set_state(FSMFillForm.add_file)

    elif message.media_group_id and message.photo is None:
        media_groups = defaultdict(list)
        logger.info("Send media_group")

        async def process_group_after_timeout(media_group_id: str):
            await asyncio.sleep(2)

        media_groups[message.media_group_id].append(message)
        asyncio.create_task(process_group_after_timeout(message.media_group_id))

        if message.media_group_id in media_groups:
            logger.info(f"Process {message.document.file_name}")
            logger.info(f'{message.document.mime_type = }')
            await message.answer(f"One of file you send - {message.document.file_name}")
            await process_single_file(message, state)

        del media_groups[message.media_group_id]

        await asyncio.sleep(3)

    elif message.document:
        logger.info("Single file")
        logger.info(f"Process single file {message.document.file_name}")
        logger.info(f'single file is {message.document.mime_type}')
        await message.answer(f"You send single file {message.document.file_name}")

        await process_single_file(message, state)

@dp.message(StateFilter(FSMFillForm.add_credit), F.text.len() < 3)
async def process_credit_sent(message: Message, state: FSMContext):
    await message.answer(text='текст не может быть короче 3 букв')
    await state.set_state(FSMFillForm.add_credit)

if __name__ == '__main__':
    async def set_main_menu():
        await bot.set_my_commands(commands=kp_uploader)

    dp.startup.register(set_main_menu)
    dp.run_polling(bot)