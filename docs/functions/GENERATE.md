🔹 Логика генерации и проверки Telegram username (на основе кода)
🔹 Общая последовательность работы
Получение входных данных

Пользователь задает контекст (context) — основу для генерации username.
Учитываются настройки из config, влияющие на процесс генерации.
Генерация списка username через OpenAI

AI получает контекст и запрос (PROMPT) и возвращает список username.
Ответ обрабатывается:
Разделение username (по запятым или пробелам).
Фильтрация по валидности (правилам Telegram).
Проверка доступности username

Telegram API (get_chat) — быстрый способ отсеять занятые username.
Fragment (check_username_via_fragment) — анализ редиректов и статусов:
Если Available → username доступен для покупки.
Если Taken или Sold → username недоступен.
Если Unavailable → возможна дополнительная проверка.
Формирование итогового списка

Отбираются подтвержденно свободные username.
Учитываются ограничения конфигурации (max попыток, макс. пустых ответов).




**********

✅ AI генерирует config.GENERATED_USERNAME_COUNT username за раз.
✅ Если все заняты, генерация повторяется до config.GEN_ATTEMPTS раз.
✅ Цель – найти config.AVAILABLE_USERNAME_COUNT свободных username.
✅ Если тайм-аут (config.GEN_TIMEOUT), бот сообщает пользователю о сбое.


🔹 4. Какие статусы сейчас попадают в список доступных?
python
Копировать
Редактировать
if result == "Свободно":
    available_usernames.add(username)
📌 Сейчас в список "доступных" попадает только "Свободно", что соответствует редиректу.

📌 Что НЕ попадает в список доступных:
❌ "Занято" (найдено в Telegram API)
❌ "Продано" (Fragment статус: "Sold")
❌ "Taken" (Fragment статус: "Taken")
❌ "Доступно для покупки" (Fragment статус: "Available")

