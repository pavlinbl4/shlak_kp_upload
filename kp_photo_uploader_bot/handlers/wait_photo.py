from pathlib import Path

from aiogram import types, Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from loguru import logger

from kp_photo_uploader_bot.check_existing_file import create_dir
from kp_photo_uploader_bot.image_converter.convert_images import convert_image_to_jpeg
from main import FSMFillForm, bot


def is_allowed_file_type(mime_type: str) -> bool:
    allowed_files_type = {'image/jpeg', 'image/png', 'image/x-tiff'}
    return mime_type in allowed_files_type


async def save_file_to_disk(file_path: str, destination_path: str) -> None:
    await bot.download_file(file_path, destination_path)


def convert_to_jpeg_if_needed(file_path: str) -> str:
    if Path(file_path).suffix.lower() not in ['.jpeg', '.jpg']:
        return convert_image_to_jpeg(file_path)
    return file_path


async def process_single_file(uploaded_file: types.Document, message: types.Message, state: FSMContext) -> None:
    try:
        file_id = uploaded_file.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path

        uploaded_images = create_dir("Uploaded_images")
        path_to_uploaded_image = f"{uploaded_images}/{uploaded_file.file_name}"
        await save_file_to_disk(file_path, path_to_uploaded_image)

        path_to_uploaded_image = convert_to_jpeg_if_needed(path_to_uploaded_image)
        await state.update_data(path_to_uploaded_image=path_to_uploaded_image)

        await message.answer(f"{hbold(message.from_user.full_name)}\n"
                             f"вы загрузили файл\n{hbold(uploaded_file.file_name)}\n"
                             f"теперь укажите автора/правообладателя снимка")
        await state.set_state(FSMFillForm.add_credit)
    except Exception as e:
        logger.error(f"Error processing file {uploaded_file.file_name}: {e}")
        await message.answer(
            f"Произошла ошибка при обработке файла {uploaded_file.file_name}. Пожалуйста, попробуйте еще раз.")


@dp.message(StateFilter(FSMFillForm.add_file))
async def handle_allowed_user_messages(message: types.Message, state: FSMContext):
    logger.info(message.document)
    if message.document is None:
        await message.answer(f"Отправьте фото «как файл», чтоб сохранить качество\n"
                             f"снимка")
        await state.set_state(FSMFillForm.add_file)
    else:
        uploaded_files = message.document if isinstance(message.document, list) else [message.document]
        for uploaded_file in uploaded_files:
            if is_allowed_file_type(uploaded_file.mime_type):
                await process_single_file(uploaded_file, message, state)
            else:
                await message.answer(f"Вы отправили недопустимый тип файла\n"
                                     f"{uploaded_file.mime_type}\n"
                                     f"я работаю только с фотографиями")
                await state.set_state(FSMFillForm.add_file)

#
# def register_handlers(dp: Dispatcher):
#     dp.register_message_handler(handle_allowed_user_messages)
