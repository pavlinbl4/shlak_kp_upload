from aiogram.types import BotCommand

kp_uploader = [
    BotCommand(command='start', description="Запустить бота"),
    BotCommand(command='help', description='Помощь'),
    BotCommand(command='add_image', description='Добавить фото'),
    BotCommand(command='cancel', description='Отмена')
]
