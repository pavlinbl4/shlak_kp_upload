from PIL import Image
import os


def convert_image_to_jpeg(path_to_file: str):
    supported_extensions = ['bmp', 'png', 'gif', 'tiff', 'webp']  # Поддерживаемые расширения
    jpeg_quality = 70  # Качество JPEG, от 1 (худшее) до 95 (лучшее)

    file_ext = os.path.splitext(path_to_file)[1][1:].lower()  # Получаем расширение файла без точки
    if file_ext in supported_extensions:
        try:
            with Image.open(path_to_file) as img:
                if img.mode == 'RGBA':
                    # Преобразуем изображение в RGB, удаляя прозрачный фон
                    img = img.convert('RGB')
                path_to_jpeg_file = path_to_file.replace(file_ext, 'jpg')
                img.save(path_to_jpeg_file, 'JPEG', quality=jpeg_quality)
                print("conversion successful")
                os.remove(path_to_file)
                print("initial file deleted")
        except Exception as e:
            print(f"conversion error : {e}")
    return path_to_jpeg_file


if __name__ == '__main__':
    print(convert_image_to_jpeg('/Users/evgeniy/PycharmProjects/shlak_kp_upload/tests/test_files/0280.tiff'))
