import asyncio
import aiohttp
import ssl
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from bs4 import BeautifulSoup
from config import REQUEST_INTERVAL



async def check_username_availability(bot: Bot, username: str) -> str:
    """Проверяет, свободен ли юзернейм в Telegram через API и Fragment."""
    print(f"\n[STEP 1] 🔎 Начинаем проверку username: @{username}")

    try:
        print("[STEP 2] 🔹 Отправляем запрос в Telegram API...")
        await bot.get_chat(f"@{username}")
        print(f"[RESULT] ❌ Имя @{username} занято (найдено через API).")
        return "Занято"

    except TelegramForbiddenError:
        print(f"[RESULT] ❌ Имя @{username} занято (бот был кикнут из чата).")
        return "Занято"

    except TelegramBadRequest as e:
        error_message = str(e).lower()
        print(f"[INFO] ❗ Ошибка API: {error_message}")

        if "chat not found" in error_message:
            print(f"[STEP 3] 🔹 Имя @{username} не найдено в API. Проверяем через Fragment...")
            return await check_username_via_fragment(username)

        print(f"[ERROR] ❗ Неожиданная ошибка API: {error_message}")
        return "Невозможно определить"

    except TelegramRetryAfter as e:
        # Когда Telegram возвращает сообщение с блокировкой (flood control)
        retry_after = e.retry_after
        print(f"⏳ Flood Control! Блокировка на {retry_after} секунд.")
        await asyncio.sleep(retry_after)  # Ждем указанное время перед продолжением
        return f"FLOOD_CONTROL:{retry_after}"  # Возвращаем информацию о времени ожидания

    # Делаем паузу между запросами (чтобы избежать превышения лимита)
    await asyncio.sleep(REQUEST_INTERVAL)  # Пауза 1 секунда между запросами


async def check_username_via_fragment(username: str) -> str:
    """Проверка статуса через Fragment. Анализирует редирект и 'Unavailable'."""
    url_username = f"https://fragment.com/username/{username}"
    url_query = f"https://fragment.com/?query={username}"

    print("[STEP 4] 🔹 Отправляем запрос к Fragment...")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url_username, ssl=ssl_context, allow_redirects=True) as response:
                final_url = str(response.url)
                # Если нас редиректит на ?query={username}, значит имя свободно (не 100%, но точнее не получается)
                if final_url == url_query:
                    print(f"[INFO] 🔹 Fragment сделал редирект на страницу поиска (Unavailable).")
                    return "Свободно"
                # Если остались на странице /username/{username}, значит нужно проверять статус
                html = await response.text()
                return await analyze_username_page(html, username)

    except aiohttp.ClientError as e:
        print(f"[ERROR] ❗ Ошибка при запросе к Fragment: {e}")
        return "Невозможно определить"


async def analyze_username_page(html: str, username: str) -> str:
    """Анализирует страницу конкретного юзернейма на Fragment."""
    soup = BeautifulSoup(html, 'html.parser')

    status_element = soup.find("span", class_="tm-section-header-status")
    if status_element:
        status_text = status_element.text.strip().lower()

        if "available" in status_text:
            print(f"[RESULT] ⚠️ Имя @{username} доступно для покупки.")
            return "Доступно для покупки"
        elif "sold" in status_text:
            print(f"[RESULT] ❌ Имя @{username} продано.")
            return "Продано"
        elif "taken" in status_text:
            print(f"[RESULT] ❌ Имя @{username} уже занято.")
            return "Занято"

    print(f"[WARNING] ⚠️ Статус Fragment (username) не определён.")
    return "Невозможно определить"



