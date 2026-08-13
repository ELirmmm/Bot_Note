## Telegram Bot для заметок и мыслей

Асинхронный Telegram-бот для удобного структурирования заметок и связанных с ними мыслей. Позволяет создавать заметки, наполнять их элементами (мыслями), редактировать, объединять несколько заметок в одну и управлять содержимым.

---

## Основные возможности и команды

Бот работает через систему состояний (FSM) и поддерживают следующий функционал:

---

### Команды работы с заметками и мыслями
command="start", 
description="Запустить бота",

command="view_minds",
description="Вывести все мысли с нумерацией (только при открытом файле)",

command="view_notes",
description="Вывести названия всех заметок с нумерацией",

command="merge",
description="Объединить содержимое двух заметок в одной",

command="note",
description="Показать конкретную мысль по её номеру (пример: note 3, только при открытом файле)",

command="edit",
description="Дополнить мысль новой строчкой (пример: edit 3, только при открытом файле)",

command="delete_mind",
description="Удалить мысль (пример: delete_mind 3, только при открытом файле)",

command="delete_note",
description="Удалить заметку (пример: delete_note имя_заметки)",

---

## Установка и запуск

### 1. Клонирование репозитория
### 2. Установка зависимостей
```bash
python3 -m venv venv
source venv/bin/activate  # Для macOS / Linux
venv\Scripts\activate   # Для Windows
pip install -r requirements.txt
```
### 3. Настройка переменных окружения
BOT_TOKEN=your_telegram_bot_token_here

### 4. Запуск бота
```bash
python main.py
```


