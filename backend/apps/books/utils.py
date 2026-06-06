import os
from io import BytesIO
from pathlib import Path
from django.conf import settings
from barcode import Code128
from barcode.writer import ImageWriter


def calculate_isbn13_check_digit(isbn):
    isbn = str(isbn).replace('-', '').replace(' ', '')
    if len(isbn) < 12:
        return None
    isbn = isbn[:12]
    total = 0
    for i, char in enumerate(isbn):
        digit = int(char)
        if i % 2 == 0:
            total += digit
        else:
            total += digit * 3
    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)


def is_valid_isbn13(isbn):
    isbn = str(isbn).replace('-', '').replace(' ', '')
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    expected_check = calculate_isbn13_check_digit(isbn[:12])
    return isbn[12] == expected_check


def normalize_isbn(isbn):
    isbn = str(isbn).replace('-', '').replace(' ', '')
    if len(isbn) == 10:
        return isbn
    if len(isbn) == 12 and isbn.isdigit():
        check = calculate_isbn13_check_digit(isbn)
        if check:
            return isbn + check
    if len(isbn) == 13 and is_valid_isbn13(isbn):
        return isbn
    return isbn


def get_barcode_dir():
    barcode_dir = Path(settings.MEDIA_ROOT) / 'book_barcodes'
    if not barcode_dir.exists():
        barcode_dir.mkdir(parents=True, exist_ok=True)
    return barcode_dir


def generate_barcode_image(isbn):
    isbn = normalize_isbn(isbn)
    barcode_dir = get_barcode_dir()
    filename = f"{isbn}.png"
    filepath = barcode_dir / filename
    
    if filepath.exists():
        return str(filepath), f"{settings.MEDIA_URL}book_barcodes/{filename}"
    
    rv = BytesIO()
    Code128(isbn, writer=ImageWriter()).write(rv)
    
    with open(filepath, 'wb') as f:
        f.write(rv.getvalue())
    
    return str(filepath), f"{settings.MEDIA_URL}book_barcodes/{filename}"


def get_barcode_url(isbn):
    isbn = normalize_isbn(isbn)
    barcode_dir = get_barcode_dir()
    filename = f"{isbn}.png"
    filepath = barcode_dir / filename
    
    if filepath.exists():
        return f"{settings.MEDIA_URL}book_barcodes/{filename}"
    
    return None


def ensure_barcode_exists(book):
    if not book.isbn:
        return None
    filepath, url = generate_barcode_image(book.isbn)
    return url
