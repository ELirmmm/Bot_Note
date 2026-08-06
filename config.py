import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env в окружение процесса
load_dotenv()

# Считываем токен из переменных окружения
TOKEN = os.getenv("TOKEN")
