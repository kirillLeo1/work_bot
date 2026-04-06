# Work Bot

Telegram-бот для звітів працівників і керівників.

## Що вміє

- реєстрація працівників і керівників
- 6 основних розділів звітів
- підрозділи для кожного розділу
- працівники не бачать чужі звіти
- керівники бачать усі звернення
- керівники можуть відповідати і закривати звернення
- до звіту можна додати 1 фото
- керівник має окрему адмін-панель і окремий режим звітів
- MySQL через `DATABASE_URL`
- автоматичне додавання нових колонок для фото у таблицю `submissions`

## ENV

```env
BOT_TOKEN=your_bot_token
DATABASE_URL=mysql+aiomysql://user:password@host:3306/database_name
ADMIN_IDS=123456789,987654321
BOT_USERNAME=your_bot_username
```

## Railway

Проєкт готовий для Railway:

- `requirements.txt`
- `Procfile`
- `runtime.txt`

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
