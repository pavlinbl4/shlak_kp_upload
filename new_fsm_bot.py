"""
Начну создавать бота заново
"""

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

TOKEN = Credentials().crazypythonbot
ALLOWED_USER_NAMES = {"PavlenkoEV", "anna44max"}

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
logger.info("Bot started to work")


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


# start polling
if __name__ == '__main__':
    async def set_main_menu():
        await bot.set_my_commands(commands=kp_uploader)


    dp.startup.register(set_main_menu)
    dp.run_polling(bot)
