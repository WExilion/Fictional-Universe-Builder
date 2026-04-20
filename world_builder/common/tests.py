from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from common.validators import NameValidator, FileSizeValidator, FileTypeValidator, GenreNameValidator, ImageURLValidator


class ValidatorTests(TestCase):
    def test_name_validator_accepts_valid_names(self):
        valid_names = ['John', 'Mary Jane', "O'Brien", 'Jean-Luc']

        for name in valid_names:
            with self.subTest(name=name):
                NameValidator(name)

    def test_name_validator_with_invalid_names(self):
        validator = NameValidator
        invalid_names = ['John123', 'Jean_Luc', 'John@', '  ', 'John--Doe', 'Mary  Jane', "O''Brien", '-John', 'John-']

        for name in invalid_names:
            with self.subTest(name=name):
                with self.assertRaisesMessage(ValidationError, validator.message):
                    validator(name)


    def test_genre_name_validator_with_valid_genres(self):
        valid_genres = ['Fantasy', 'Sci-Fi', 'Slice of Life']
        for genre in valid_genres:
            with self.subTest(genre=genre):
                GenreNameValidator(genre)

    def test_genre_name_validator_with_invalid_genres(self):
        validator = GenreNameValidator
        invalid_genres = ['Fantasy123', 'Sci_Fi', 'Sci--Fi', 'Sci  Fi', '-Fantasy', 'Fantasy-', ' Sci-Fi', 'Sci-Fi ']

        for genre in invalid_genres:
            with self.subTest(genre=genre):
                with self.assertRaisesMessage(ValidationError, validator.message):
                    validator(genre)


    def test_image_url_validator_accepts_valid_image_urls(self):
        validator = ImageURLValidator()

        valid_urls = [
            'https://example.com/image.jpg',
            'https://example.com/image.jpeg',
            'https://example.com/image.png',
            'https://example.com/image.webp',
            'https://example.com/path/to/image.PNG',
            'https://example.com/image.jpg?size=large',
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                validator(url)

    def test_image_url_validator_rejects_invalid_urls(self):
        validator = ImageURLValidator()

        invalid_urls = [
            'https://example.com/image',
            'https://example.com/image.txt',
            'https://example.com/image.jpg/extra',
            'https://example.com/page?image=photo.jpg',
            'not-a-url',
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaisesMessage(ValidationError, validator.message):
                    validator(url)


    def test_file_type_validator_accepts_valid_types(self):
        validator = FileTypeValidator(allowed_types=['jpg', 'png', 'webp'])

        valid_files = [
            ('jpg', SimpleUploadedFile('test.jpg', b'\xff\xd8\xff' + b'0' * 10)),
            ('png', SimpleUploadedFile('test.png', b'\x89PNG' + b'0' * 10)),
            ('webp', SimpleUploadedFile('test.webp', b'RIFF' + b'0000' + b'WEBP' + b'0' * 4)),
        ]
        for file_type, file in valid_files:
            with self.subTest(file_type=file_type):
                validator(file)

    def test_file_type_validator_with_invalid_type(self):
        validator = FileTypeValidator(allowed_types=['jpg', 'png'])

        invalid_file = SimpleUploadedFile('test.txt', b'This is a text file')
        with self.assertRaisesMessage(ValidationError, validator.message):
            validator(invalid_file)

    def test_file_type_validator_rejects_file_with_valid_extension_but_invalid_content(self):
        validator = FileTypeValidator(allowed_types=['jpg', 'png'])

        fake_jpg = SimpleUploadedFile('test.jpg', b'This is not really an image')

        with self.assertRaisesMessage(ValidationError, validator.message):
            validator(fake_jpg)

    def test_file_type_validator_resets_file_pointer(self):
        validator = FileTypeValidator(allowed_types=['jpg'])

        file = SimpleUploadedFile('test.jpg', b'\xff\xd8\xff' + b'0' * 10)
        validator(file)

        self.assertEqual(file.tell(), 0)



    def test_file_size_validator_within_limit(self): # noqa
        validator = FileSizeValidator(file_size_mb=1)
        file = SimpleUploadedFile('test.jpg', b'0' * (512 * 1024))

        validator(file)

    def test_file_size_validator_allows_file_at_exact_limit(self): # noqa
        validator = FileSizeValidator(file_size_mb=1)
        file = SimpleUploadedFile('test.jpg', b'0' * (1024 * 1024))

        validator(file)

    def test_file_size_validator_exceeds_limit(self):
        validator = FileSizeValidator(file_size_mb=1)
        file = SimpleUploadedFile('test.jpg', b'0' * (1536 * 1024))

        with self.assertRaisesMessage(ValidationError, validator.message):
            validator(file)



