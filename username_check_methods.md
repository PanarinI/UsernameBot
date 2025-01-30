📌 1. Логика работы кода
Алгоритм проверки username состоит из трёх ключевых этапов:

🔹 1. Обработка команды /check [username]
Бот получает команду /check username.
Проверяет, соответствует ли username требованиям (буквы, цифры, _, длина 5-32).
Если формат некорректен → отправляет ошибку пользователю.
🔹 2. Проверка через Telegram Bot API (bot.get_chat(username))
Бот отправляет запрос в API.
Если API нашло чат → Имя занято.
Если API не нашло (chat not found) → Идём проверять t.me/{username}.
🔹 3. Проверка через t.me/{username}
Бот делает HTTP-запрос к t.me/{username}.
Если сервер вернул 404 → Имя свободно.
Если в HTML есть tgme_page_title или "If you have Telegram, you can contact" → Имя занято.
Если в <title> есть "Telegram: Contact @username", но tgme_page_title отсутствует → Имя свободно.
Если Telegram дал странный HTML-код → "Невозможно определить".


***********


Можно ли проверить, занят ли юзернейм в Telegram через бота?
✅ Да, это возможно, но есть ограничения.
❌ Telegram не предоставляет официального API для проверки, свободен ли username.

Но есть обходные пути:

Способ 1: Пробуем найти пользователя через get_chat() (лучший вариант).
Способ 2: Используем сторонние сервисы (не рекомендуем).
Способ 3: Проверяем по URL (ненадежный метод).
📌 Способ 1: Используем get_chat()
В aiogram есть метод get_chat(username), который возвращает информацию о пользователе, если он существует.

🔹 Как это работает?

Если пользователь существует, API вернёт объект Chat.
Если username свободен, бот получит ошибку.
✅ Реализация check_username_availability()
python
Копировать
Редактировать
from aiogram import Bot
from aiogram.utils.exceptions import BadRequest

bot = Bot(token="YOUR_BOT_TOKEN")  # Замените на свой токен

async def check_username_availability(username: str) -> bool:
    """Проверяет, занят ли юзернейм в Telegram."""
    try:
        await bot.get_chat(f"@{username}")  # Пробуем найти пользователя
        return False  # Пользователь найден → имя занято
    except BadRequest:
        return True  # Ошибка → имя свободно
🔹 Как это работает?
bot.get_chat(f"@{username}") → пробуем получить информацию о пользователе.
Если username существует, API вернёт данные → значит, имя занято (return False).
Если username не существует, Telegram выдаст ошибку BadRequest, значит, имя свободно (return True).
📌 Полный код бота с /check
Теперь можно использовать этот метод в обработчике:

python
Копировать
Редактировать
from aiogram import Bot, Dispatcher, types
from aiogram.utils.exceptions import BadRequest
from aiogram.types import Message
from aiogram.utils import executor

TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def check_username_availability(username: str) -> bool:
    """Проверяет, свободен ли юзернейм в Telegram."""
    try:
        await bot.get_chat(f"@{username}")
        return False  # Имя занято
    except BadRequest:
        return True  # Имя свободно

@dp.message_handler(commands=['check'])
async def check(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Использование: /check [username]")
        return
    
    username = args[1].replace("@", "")

    if not username.isalnum() or len(username) < 5 or len(username) > 32:
        await message.reply("❌ Ошибка: имя должно содержать только буквы и цифры, от 5 до 32 символов.")
        return

    is_available = await check_username_availability(username)

    if is_available:
        await message.reply(f"✅ Имя @{username} свободно!")
    else:
        await message.reply(f"❌ Имя @{username} уже занято.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
📌 Способ 2: Используем сторонние сервисы (не рекомендуется)
Некоторые сайты предоставляют API для проверки, например:

https://t.me/{username} (но это ненадёжно).
Неофициальные API (их могут заблокировать).
Можно проверить username через requests.get():

python
Копировать
Редактировать
import requests

def check_username_availability(username: str) -> bool:
    url = f"https://t.me/{username}"
    response = requests.get(url)
    return response.status_code == 404  # Если 404, значит, имя свободно
❌ Минусы:

Telegram может блокировать такие запросы.
Ненадёжный метод.
📌 Способ 3: Проверка по URL (не всегда точная)
Можно попробовать открыть ссылку https://t.me/{username} и проверить, есть ли там профиль.
Но это не точный метод:

Если пользователь скрыл свой профиль, URL всё равно будет доступен.
Если аккаунт заблокирован, имя может быть занято, но не найдено.
Пример:

python
Копировать
Редактировать
import requests

def check_username_availability(username: str) -> bool:
    url = f"https://t.me/{username}"
    response = requests.get(url)
    return response.status_code == 404
📌 Какой способ лучше?
Метод	Надёжность	Простота	Минусы
✅ bot.get_chat()	👍 Надёжный	😃 Легко реализовать	🚫 Работает только в ботах
❌ Запрос на https://t.me/username	😕 Не всегда точный	🙂 Просто	🚫 Может вернуть неправильный результат
❌ Сторонние API	😕 Ненадёжно	🤷‍♂️ API могут закрыть	🚫 Можно получить бан
Вывод:
✅ Лучший вариант — использовать bot.get_chat().
❌ Другие способы ненадёжны и могут дать неверные результаты.