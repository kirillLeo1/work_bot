# Telegram bot для звітів працівників

Готовий проєкт під Railway + MySQL.

## Що вміє
- реєстрація працівника або керівника через `/start`
- 6 головних кнопок працівника:
  - Звіт за день
  - Закупівля
  - Витрати
  - Продажі
  - Склад
  - Проблеми виробництва
- підкатегорії за твоєю схемою
- усі звернення зберігаються в MySQL
- інші працівники не бачать чужі повідомлення
- керівники бачать усе в адмінці
- керівники можуть:
  - дивитися нові звернення
  - дивитися всі звернення
  - дивитися історію по працівнику
  - відповідати працівнику
  - закривати звернення

## ENV
Створи `.env` або встав змінні в Railway:

```env
BOT_TOKEN=your_bot_token_here
DATABASE_URL=mysql+aiomysql://user:password@host:3306/database_name
ADMIN_IDS=111111111,222222222
BOT_USERNAME=
```

## Де взяти ADMIN_IDS
Напиши будь-якому боту типу `@userinfobot`, він покаже твій Telegram ID.

## Railway
1. Завантаж проєкт у GitHub.
2. Підключи репозиторій у Railway.
3. Додай ENV змінні.
4. Переконайся, що є MySQL база.
5. Запускай.

## Локальний запуск
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Важливо
Формат `DATABASE_URL` має бути саме SQLAlchemy async:

```env
mysql+aiomysql://user:password@host:3306/database_name
```

Якщо Railway дає тобі звичайний mysql URL, просто додай `+aiomysql` після `mysql`.

Було:
```env
mysql://user:password@host:3306/database_name
```

Стає:
```env
mysql+aiomysql://user:password@host:3306/database_name
```
