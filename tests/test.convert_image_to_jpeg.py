import unittest
import os
from PIL import Image
from tempfile import TemporaryDirectory
from kp_photo_uploader_bot.image_converter.convert_images import convert_image_to_jpeg


class TestConvertImageToJpeg(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.input_files = {
            'image_bmp.bmp': Image.new('RGB', (100, 100)),
            'image_png.png': Image.new('RGB', (100, 100)),
            'image_gif.gif': Image.new('RGB', (100, 100)),
            'image_tiff.tiff': Image.new('RGB', (100, 100)),
            'image_webp.webp': Image.new('RGB', (100, 100))
        }
        for filename, img in self.input_files.items():
            img.save(os.path.join(self.temp_dir.name, filename))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_convert_image_to_jpeg(self):
        for filename, img in self.input_files.items():
            file_ext = os.path.splitext(filename)[1][1:].lower()
            expected_jpeg_filename = os.path.join(self.temp_dir.name, f"{os.path.splitext(filename)[0]}.JPG")

            converted_jpeg_path = convert_image_to_jpeg(os.path.join(self.temp_dir.name, filename))
            self.assertEqual(converted_jpeg_path, expected_jpeg_filename)

            with Image.open(expected_jpeg_filename) as jpeg_img:
                self.assertEqual(jpeg_img.mode, 'RGB')
                self.assertNotIn('A', jpeg_img.getbands())  # Ensure no alpha channel

            self.assertTrue(os.path.exists(expected_jpeg_filename))
            self.assertFalse(os.path.exists(os.path.join(self.temp_dir.name, filename)))

    def test_invalid_file_extension(self):
        invalid_file_path = os.path.join(self.temp_dir.name, 'invalid_file.txt')
        with open(invalid_file_path, 'w') as f:
            f.write("This is a text file.")

        converted_jpeg_path = convert_image_to_jpeg(invalid_file_path)
        self.assertIsNone(converted_jpeg_path)
        self.assertTrue(os.path.exists(invalid_file_path))  # Original file should not be deleted


if __name__ == '__main__':
    unittest.main()
