import string
from secrets import choice

def generate_id() -> str:
    """
    Генерирует последовательность из 10 случайных
    символов (буквы + цифры)
    """
    chars = string.ascii_letters + string.digits
    return ''.join(choice(chars) for _ in range(10))

