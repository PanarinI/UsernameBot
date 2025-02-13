База - это коллекция сгенерированных ползователями ответов.
Автоматически собирает сгенерированные username и  связанные параметры: status, category, context.
Category - эт категория, сгенерированная AI исходя из контекста




📌 Таблица generated_usernames
Поле	Тип данных	Описание
id	SERIAL PRIMARY KEY	Уникальный идентификатор записи
username	VARCHAR(32) UNIQUE	Сам сгенерированный username
status	TEXT	Статус (Свободно, Занято, Продано, Доступно для покупки, Невозможно определить)
tag	TEXT	Категория (например, бизнес, развлечения, технологии и т. д.)
context	TEXT	Исходный запрос пользователя
created_at	TIMESTAMP DEFAULT CURRENT_TIMESTAMP	Дата и время генерации


✅ Преимущества такой структуры:

Можно анализировать все username, даже те, что были заняты.
Можно делать статистику по категориям (SELECT tag, COUNT(*) FROM generated_usernames GROUP BY tag).
Можно исключать уже сгенерированные имена, чтобы AI не повторял их (SELECT username FROM generated_usernames WHERE status = 'Свободно').
Можно добавить аналитические инструменты в будущем.


📌 Общий алгоритм записи в БД:

Пользователь вводит запрос → AI генерирует username.
Каждый username проверяется на занятость (API Telegram → Fragment).
Все username + их статусы записываются в БД (включая занятые).
AI присваивает каждому username категорию (тэг) и тоже записывает в БД.
Только свободные username показываются пользователю.



async def connect_to_db():
    return await asyncpg.connect(
        database="my_telegram_bot",  # Название базы данных
        user="my_user",              # Имя пользователя PostgreSQL
        password="my_password",      # Пароль пользователя
        host="localhost"             # Сервер (если локально — localhost)
    )







Генерируем username (AI) → generate_usernames(context)
Получаем тэг от AI (определяем категорию)
Проверяем username через API → check_username_availability(bot, username)
Записываем в БД:

INSERT INTO generated_usernames (username, status, tag, created_at)
VALUES ('ArchNova', 'Свободно', 'бизнес', NOW());







1️⃣ Откуда берём username?

usernames = await generate_usernames(context, n=config.GENERATED_USERNAME_COUNT) 

ловим момент генерации и сразу записываем в базу.

2️⃣ Откуда берём статус username?
result = await check_username_availability(bot, username)
запишем username в БД сразу после проверки, сохранив его статус.

3️⃣ Как формируем тэг (категорию)?
 AI сам анализирует контекст и возвращает тэг.

Вместо одной задачи "Придумай username" в промпт добавляется "Определи категорию".
OpenAI API возвращает не только username, но и тэг:

{
  "usernames": ["ArchNova", "UrbanStyle"],
  "tag": "бизнес"
}



