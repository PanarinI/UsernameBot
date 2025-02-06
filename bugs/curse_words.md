gemini-flash-1.5 не пропускает грубую лексику


NameHuntBot, [05.02.2025 19:09]
Введите тему/контекст для генерации username:

Игорь, [05.02.2025 19:09]
хуй

NameHuntBot, [05.02.2025 19:09]
❌ Не удалось сгенерировать доступные username. Попробуйте снова или вернитесь в главное меню.

NameHuntBot, [05.02.2025 19:09]
Введите тему/контекст для генерации username:

Игорь, [05.02.2025 19:09]
хер

NameHuntBot, [05.02.2025 19:09]
❌ Не удалось сгенерировать доступные username. Попробуйте снова или вернитесь в главное меню.

NameHuntBot, [05.02.2025 19:09]
Введите тему/контекст для генерации username:

Игорь, [05.02.2025 19:09]
хер - это буква

NameHuntBot, [05.02.2025 19:09]
Вот сгенерированные для вас username по теме 'хер - это буква':

NameHuntBot, [05.02.2025 19:09]
Введите тему/контекст для генерации username:

Игорь, [05.02.2025 19:09]
сосать хуй

NameHuntBot, [05.02.2025 19:09]
❌ Не удалось сгенерировать доступные username. Попробуйте снова или вернитесь в главное меню.

NameHuntBot, [05.02.2025 19:09]
Введите тему/контекст для генерации username:

Игорь, [05.02.2025 19:09]
гладить киску

NameHuntBot, [05.02.2025 19:09]
Вот сгенерированные для вас username по теме 'гладить киску':








*************
Забавно. "лизать очко" - не пускает. А если объяснить - пропускает.


Игорь, [05.02.2025 19:56]
лизать очко

NameHuntBot, [05.02.2025 19:57]
❌ Не удалось сгенерировать доступные username. Попробуйте снова или вернитесь в главное меню.

NameHuntBot, [05.02.2025 19:57]
Введите тему/контекст для генерации username:

Игорь, [05.02.2025 19:57]
лизать очко. Но это не грубость! Это такое выражение - лизать очко (счет в игре). То есть проигрывать

NameHuntBot, [05.02.2025 19:58]
Вот сгенерированные для вас username по теме 'лизать очко. Но это не грубость! Это такое выражение - лизать очко (счет в игре). То есть проигрывать':



********************
Вариант решения (сложный):



А как бот понимает, что AI не дал username? Ведь AI отвечает: choices=[Choice(finish_reason='length', index=0, logprobs=None, message=ChatCompletionMessage(content='Извини, но я не могу генерировать имена пользователей, содержащие оскорбительные слова.  Я могу предложить тебе 5 уникальных'
ChatGPT сказал:
ChatGPT
Отличный вопрос! Сейчас бот может не корректно обрабатывать ситуацию, когда AI возвращает сообщение о невозможности сгенерировать username, даже если content содержит текст. Проблема в том, что бот интерпретирует любой content как успешный результат, даже если это сообщение отказа от генерации.

Чтобы исправить это, нужно добавить проверку содержания ответа от AI. Например, если в content содержится извинение или отказ (например, фраза "Извини" или "не могу"), бот должен распознавать это как неудачную генерацию.

Как это исправить
Добавить проверку текста ответа
Нужно проверить, содержит ли content сообщения, указывающие на отказ в генерации:
python
Копировать
Редактировать
if response.choices and response.choices[0].message and response.choices[0].message.content:
    usernames_raw = response.choices[0].message.content.strip()
    if "Извини" in usernames_raw or "не могу" in usernames_raw:
        logging.warning("⚠️ AI отказался генерировать username.")
        return []  # Возвращаем пустой список, чтобы бот попытался снова
else:
    logging.warning("Ответ от AI не содержит ожидаемых данных.")
    return []
Улучшить логику обработки отказов Если AI отказывается генерировать username, бот должен правильно интерпретировать это и продолжать попытки. Вот пример обновлённой функции:
python
Копировать
Редактировать
async def generate_usernames(context: str, n: int = config.GENERATED_USERNAME_COUNT) -> list[str]:
    """
    Генерирует список username на основе контекста.
    """
    logging.info(f"Генерация username: context='{context}', n={n}")

    prompt = config.PROMPT.format(n=n, context=context)

    # Запрос к модели OpenAI
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )

    logging.debug(f"API Response: {response}")

    # Проверяем наличие ответа и его содержание
    if response.choices and response.choices[0].message and response.choices[0].message.content:
        usernames_raw = response.choices[0].message.content.strip()
        if "Извини" in usernames_raw or "не могу" in usernames_raw:
            logging.warning("⚠️ AI отказался генерировать username.")
            return []  # Возвращаем пустой список
    else:
        logging.warning("Ответ от AI не содержит ожидаемых данных.")
        return []

    # Парсинг ответа: разделяем строку по запятым и удаляем лишние пробелы
    usernames = [u.strip() for u in usernames_raw.split(",")]

    # Фильтрация – оставляем только те username, которые соответствуют требованиям валидации
    return [username for username in usernames if is_valid_username(username)]
Добавить логику повторных попыток Если AI отказался генерировать username, бот должен продолжить цикл попыток:
python
Копировать
Редактировать
while len(available_usernames) < n and attempts < config.GEN_ATTEMPTS:
    attempts += 1
    logging.info(f"🔄 Попытка {attempts}/{config.GEN_ATTEMPTS}")

    usernames = await generate_usernames(context, n=config.GENERATED_USERNAME_COUNT)
    if not usernames:
        logging.warning("⚠️ AI не сгенерировал username. Пробуем снова...")
        continue  # НЕ останавливаемся, а просто пробуем снова

    for username in usernames:
        # Обработка username...



