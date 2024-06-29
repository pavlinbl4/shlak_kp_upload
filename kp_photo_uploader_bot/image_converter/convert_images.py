import sys

from loguru import logger

from PIL import Image
import os

# logger.add("output.log", format="{time} {level} {message}", level="INFO")
logger.add(sys.stdout, level="INFO")


def convert_image_to_jpeg(path_to_file: str):
    logger.info(path_to_file)
    supported_extensions = ['bmp', 'png', 'gif', 'tiff', 'webp']  # Поддерживаемые расширения
    jpeg_quality = 70  # Качество JPEG, от 1 (худшее) до 95 (лучшее)

    file_ext = os.path.splitext(path_to_file)[1][1:].lower()  # Получаем расширение файла без точки
    logger.info(file_ext)
    if file_ext in supported_extensions:
        logger.info(f' allowed file extension\n{path_to_file}')
        try:
            with Image.open(path_to_file) as img:
                logger.info(f'initial image mode {img.mode}')
                if img.mode == 'RGBA':
                    # Преобразуем изображение в RGB, удаляя прозрачный фон
                    img = img.convert('RGB')
                logger.info(f' image mode after converse {img.mode}')
                path_to_jpeg_file = path_to_file.replace(file_ext, 'JPG')
                logger.info(path_to_jpeg_file)
                img.save(path_to_jpeg_file, 'JPEG', quality=jpeg_quality)
                logger.info("conversion successful")
                os.remove(path_to_file)
                logger.info("initial file deleted")
        except Exception as e:
            logger.error(f"conversion error :\n{e}")
    return path_to_jpeg_file


def convert_images_in_folder_to_jpeg(directory_path):
    supported_extensions = ['bmp', 'png', 'gif', 'tiff', 'webp']  # Поддерживаемые расширения
    jpeg_quality = 70  # Качество JPEG, от 1 (худшее) до 95 (лучшее)

    for filename in os.listdir(directory_path):
        file_ext = os.path.splitext(filename)[1][1:].lower()  # Получаем расширение файла без точки
        if file_ext in supported_extensions:
            file_path = os.path.join(directory_path, filename)
            try:
                with Image.open(file_path) as img:
                    if img.mode == 'RGBA':
                        # Преобразуем изображение в RGB, удаляя прозрачный фон
                        img = img.convert('RGB')

                    img.save(file_path.replace(file_ext, '.jpg'), 'JPEG', quality=jpeg_quality)
                    print(f"{filename} успешно конвертирован в JPEG.")
            except Exception as e:
                print(f"Ошибка при конвертации файла {filename}: {e}")


if __name__ == '__main__':
    convert_image_to_jpeg('/Users/evgeniy/Desktop/ScreenShorts/Screenshot 2024-03-10 at 21.29.40.png')
