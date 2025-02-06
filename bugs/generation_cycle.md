# Анализ проблемы и рекомендации по её устранению

## Проблема
При генерации [gen=2, avail=5] генерируется [name.free[1] + name1.busy] > [name2_free[2] + name1.busy] > name1.busy > name1.busy ... > name1.busy 
Гипотеза - возникает когда сгенерирован username, идентичный сгенерированному занятому.


[STEP 1] 🔎 Проверяем username: @NewYearPuns
[STEP 2] 🔹 Запрос в Telegram API...
[INFO] ❗ Ошибка API: telegram server says - bad request: chat not found
[STEP 3] 🔹 Имя @NewYearPuns не найдено в API. Проверяем через t.me...
[STEP 4] 🔹 Запрос к t.me...
[RESULT] ✅ Имя @NewYearPuns свободно (по заголовку).

[STEP 1] 🔎 Проверяем username: @XmasJokes
[STEP 2] 🔹 Запрос в Telegram API...
[RESULT] ❌ Имя @XmasJokes занято (API).

[STEP 1] 🔎 Проверяем username: @XmasJokeMaster
[STEP 2] 🔹 Запрос в Telegram API...
[INFO] ❗ Ошибка API: telegram server says - bad request: chat not found
[STEP 3] 🔹 Имя @XmasJokeMaster не найдено в API. Проверяем через t.me...
[STEP 4] 🔹 Запрос к t.me...
[RESULT] ✅ Имя @XmasJokeMaster свободно (по заголовку).

[STEP 1] 🔎 Проверяем username: @XmasJokes
[STEP 2] 🔹 Запрос в Telegram API...
[RESULT] ❌ Имя @XmasJokes занято (API).

[STEP 1] 🔎 Проверяем username: @XmasJokes
[STEP 2] 🔹 Запрос в Telegram API...
[RESULT] ❌ Имя @XmasJokes занято (API).




Вы столкнулись с ситуацией, когда:
- **Конфигурация:**  
  - `GENERATED_USERNAME_COUNT = 2` (за один запрос к API генерируется 2 варианта)  
  - `AVAILABLE_USERNAME_COUNT = 5` (необходимо собрать 5 уникальных доступных вариантов)

- **Сценарий:**  
  API возвращает, например, список `['NewYearPuns', 'XmasJokes']`. При этом:
  - `NewYearPuns` (если доступен) добавляется в итоговый набор.
  - `XmasJokes` оказывается занятым.
  
  Если API в следующих запросах продолжает возвращать тот же самый список (или повторяющиеся варианты, среди которых есть занятые), то условие `while len(available_usernames) < n` никогда не будет выполнено. В результате происходит **бесконечное выполнение цикла** с повторными вызовами API, что приводит к:
  - Избыточным расходам токенов (и, соответственно, денег).
  - Потенциальным задержкам и нагрузке на систему.

## Почему это происходит

1. **Маленький размер генерируемой партии:**  
   При вызове API возвращается всего 2 варианта. Если оба варианта повторяются или не удовлетворяют условию доступности, то для получения 5 уникальных вариантов приходится делать повторные запросы.

2. **Отсутствие механизма контроля повторов:**  
   Если один и тот же занятый вариант (например, `XmasJokes`) постоянно генерируется, его проверка производится снова и снова, так как нет механизма, который бы отслеживал уже проверенные (и заведомо недоступные) варианты.

3. **Полное пересоздание списка:**  
   Каждый раз вызывается API, даже если в предыдущих итерациях уже были получены одни и те же варианты. Это приводит к постоянной трате ресурсов.

## Рекомендации по исправлению

### 1. Введение защиты от бесконечного цикла

- **Максимальное число итераций:**  
  Добавьте счётчик итераций или лимит вызовов API. Если лимит исчерпан, можно вернуть имеющийся набор (или сообщить о невозможности найти требуемое количество вариантов).

- **Отслеживание уже проверенных username:**  
  Ведите отдельное множество (например, `attempted_usernames`), чтобы не повторять проверки для уже заведомо недоступных вариантов.  
  Пример:
  ```python
  attempted_usernames = set()
  
  while len(available_usernames) < n and iterations < MAX_ITERATIONS:
      usernames = await generate_usernames(context, n=config.GENERATED_USERNAME_COUNT)
      for username in usernames:
          if username in attempted_usernames:
              continue
          attempted_usernames.add(username)
          result = await check_username_availability(bot, username)
          if result == "Свободно":
              available_usernames.add(username)
              if len(available_usernames) >= n:
                  break
      iterations += 1



2. Оптимизация расхода токенов
Адаптивный размер партии:
Вместо фиксированного GENERATED_USERNAME_COUNT = 2 можно сделать размер партии адаптивным:
Если предыдущий вызов не дал достаточного количества новых вариантов, увеличивайте размер партии (например, до 4 или 6), чтобы увеличить разнообразие вариантов.
Если API возвращает слишком много вариантов (и токенов тратится много), можно уменьшать размер партии.
Оптимизация запроса к API:
Постарайтесь сформулировать prompt так, чтобы API возвращал более разнообразные варианты. Возможно, добавьте случайный элемент или изменяйте формулировку запроса, 
чтобы снизить вероятность повторения уже известных вариантов.






# Решение: Глобальный "рубильник" для защиты от бесконечных запросов к AI API

Чтобы гарантировать, что пользователь не застрянет в режиме ожидания (например, из-за зацикливания или долгих зависаний вызова API), можно реализовать два механизма защиты:

1. **Лимит попыток (attempts limit):**  
   Добавляем в конфигурацию параметр, который ограничивает максимальное число вызовов (или итераций цикла), после которого дальнейшие запросы к AI API прекращаются. Если лимит превышен, функция должна завершиться – например, вернуть пустой список или специальное значение, сигнализируя, что генерация не удалась, и затем вывести сообщение пользователю.

2. **Глобальный таймаут:**  
   Можно обернуть вызов генерации в `asyncio.wait_for`, чтобы при длительном ожидании (например, более 60 секунд) процесс был прерван и пользователь получил ответ об ошибке.

## Пример изменений в конфигурации

В файле `config.py` добавьте два новых параметра:

# Максимальное количество итераций (попыток) генерации username
MAX_GENERATION_ATTEMPTS = 10

# Максимальное время ожидания генерации (в секундах)
MAX_GENERATION_TIMEOUT = 60




****************
Тест: 
GEN=1
AVAIL=5

Проблема:
Зависание на состоянии после ввода

log:
  File "F:\PythonProject\UsernameBot\bot\handlers\generate.py", line 42, in process_context_input
    reply_markup=main_menu())
                 ^^^^^^^^^
NameError: name 'main_menu' is not defined



****************
Тест: 
GEN=2
AVAIL=4

Проблема:
Вывел только один вариант. Вижу причину в том,что дважды одинаковое имя

[STEP 1] 🔎 Проверяем username: @zh_opa_helper
[STEP 2] 🔹 Запрос в Telegram API...
[INFO] ❗ Ошибка API: telegram server says - bad request: chat not found
[STEP 3] 🔹 Имя @zh_opa_helper не найдено в API. Проверяем через t.me...
[STEP 4] 🔹 Запрос к t.me...
[RESULT] ✅ Имя @zh_opa_helper свободно (по заголовку).

[STEP 1] 🔎 Проверяем username: @butt_detective
[STEP 2] 🔹 Запрос в Telegram API...
[RESULT] ❌ Имя @butt_detective занято (API).

[STEP 1] 🔎 Проверяем username: @butt_detective
[STEP 2] 🔹 Запрос в Telegram API...
[RESULT] ❌ Имя @butt_detective занято (API).

log:
2025-02-05 19:16:22,214 - DEBUG - API Response: ChatCompletion(id='gen-1738772182-NifTfYjGcoM14XMlNulh', 
choices=[Choice(finish_reason='length', index=0, logprobs=None, message=ChatCompletionMessage(content='Заданный контекст не подходит для создания юзернеймов.  
Нельзя создавать юзернеймы, которые являются оскорбительными или непри', refusal=None, role='assistant', audio=None, function_call=None, tool_calls=None, reasoning=None), 
native_finish_reason='MAX_TOKENS')], created=1738772182, model='google/gemini-flash-1.5', object='chat.completion', service_tier=None, system_fingerprint=None, 
usage=CompletionUsage(completion_tokens=30, prompt_tokens=98, total_tokens=128, completion_tokens_details=None, prompt_tokens_details=None, cache_discount_rub=0, 
cost_rub=0.01, balance=126.66000000000207))


Разбор проблемы^
Ты ожидал 4 уникальных доступных username (AVAILABLE_USERNAME_COUNT = 4), но в итоге получил только 1.

📌 Разбираем поведение бота:

AI сгенерировал 2 username (GENERATED_USERNAME_COUNT = 2):

✅ zh_opa_helper → свободен
❌ butt_detective → занят
Бот отправил повторный запрос, потому что ему нужно было ещё 3 username.

AI снова сгенерировал те же самые username.
zh_opa_helper уже есть, butt_detective всё ещё занят.
Бот должен был продолжать генерацию, но остановился после второго запроса.

В третьей генерации AI отказался генерировать username из-за неприемлемого контекста:

arduino
Копировать
Редактировать
"Заданный контекст не подходит для создания юзернеймов."
📌 Итог:

GEN_ATTEMPTS = 10 не сработали, потому что бот остановился после второй неудачи.
AI сгенерировал один и тот же занятый username → бот не смог набрать 4 доступных.




Тест:

GEN=2
AVAIL=4

Проблема:
Вывел 2 вместо четырех

Контекст: жопа

[STEP 1] 🔎 Проверяем username: @zh_opa_helper
[STEP 2] 🔹 Запрос в Telegram API...
[INFO] ❗ Ошибка API: telegram server says - bad request: chat not found
[STEP 3] 🔹 Имя @zh_opa_helper не найдено в API. Проверяем через t.me...
[STEP 4] 🔹 Запрос к t.me...
[RESULT] ✅ Имя @zh_opa_helper свободно (по заголовку).

[STEP 1] 🔎 Проверяем username: @butt_detective
[STEP 2] 🔹 Запрос в Telegram API...
[RESULT] ❌ Имя @butt_detective занято (API).

[STEP 1] 🔎 Проверяем username: @butt_detective
[STEP 2] 🔹 Запрос в Telegram API...
[RESULT] ❌ Имя @butt_detective занято (API).

[STEP 1] 🔎 Проверяем username: @butt_detective
[STEP 2] 🔹 Запрос в Telegram API...
[RESULT] ❌ Имя @butt_detective занято (API).

[STEP 1] 🔎 Проверяем username: @butt_alert_bot
[STEP 2] 🔹 Запрос в Telegram API...
[INFO] ❗ Ошибка API: telegram server says - bad request: chat not found
[STEP 3] 🔹 Имя @butt_alert_bot не найдено в API. Проверяем через t.me...
[STEP 4] 🔹 Запрос к t.me...


Проблема: НЕ ФИЛЬТРУЕТ УЖЕ ПРОВЕРЕННЫЕ USERNAME

Что произошло и почему вывелось только два username?
1️⃣ Разбор логики работы
Ты задал AVAILABLE_USERNAME_COUNT = 4 (нужно найти 4 доступных username).
Бот генерирует GENERATED_USERNAME_COUNT = 2 (генерирует по 2 username за один запрос к AI).
Лимит генераций GEN_ATTEMPTS = 10 (бот попробует 10 раз сгенерировать username, если их не хватает).
2️⃣ Как шёл процесс генерации
Первая генерация

AI сгенерировал zh_opa_helper и butt_alert_bot.
Проверка доступности:
zh_opa_helper → Свободно ✅
butt_alert_bot → Свободно ✅
Теперь у нас 2 свободных username, но нам нужно 4.
Вторая генерация

AI снова сгенерировал те же username (zh_opa_helper, butt_alert_bot).
Проверка доступности:
butt_alert_bot (повторно) → Занято ❌
Ничего нового не добавилось ❌
Третья генерация

AI сгенерировал: butt_detective (занято ❌).
Опять нет нового свободного имени ❌.
Четвёртая генерация (и последующие до 10-й попытки)

AI отказывается генерировать username (он считает контекст "жопа" неуместным).
Мы получаем в API-ответе length или MAX_TOKENS, что означает, что AI отказался давать новые варианты.
3️⃣ Почему получилось только 2 имени?
Мы достигли лимита попыток GEN_ATTEMPTS = 10, но AI перестал генерировать новые username.
Если AI не даёт новые username, мы не можем найти 4 доступных username, даже если GEN_ATTEMPTS позволяет продолжать.
Вывод: цикл закончился, потому что бот исчерпал попытки генерации.
✅ Как исправить?
1️⃣ Изменить стратегию генерации
Текущий алгоритм:

Генерируем 2 username за раз.
Если хотя бы 1 из них занят, делаем новую генерацию.
Но если AI отказывается давать новые варианты, бот застревает и теряет попытки впустую.
Решение:

Генерировать больше username за 1 запрос, например, GENERATED_USERNAME_COUNT = 4.
Фильтровать повторяющиеся username (AI часто повторяет их).
Если AI несколько раз подряд отказывается генерировать новые username, прекращать попытки раньше, а не ждать 10 попыток.