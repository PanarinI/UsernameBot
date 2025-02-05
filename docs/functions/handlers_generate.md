Скрипт handlers/generate.py отвечает за:

Обработку команды "Сгенерировать username".

Получение контекста от пользователя.

Генерацию и проверку доступности username.

Вывод результата пользователю через клавиатуру.

Импорты
python
Copy
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from services.generate import get_available_usernames
from keyboards.generate import generate_username_kb
Router: Используется для создания роутера, который будет обрабатывать команды и сообщения.

types: Содержит типы данных Aiogram (например, Message, CallbackQuery).

F: Фильтры для обработки сообщений и колбэков.

FSMContext: Контекст конечного автомата (Finite State Machine), который помогает управлять состояниями бота.

get_available_usernames: Функция из services/generate.py, которая генерирует и проверяет доступность username.

generate_username_kb: Функция из keyboards/generate.py, которая создаёт клавиатуру с сгенерированными username.

Создание роутера
python
Copy
generate_router = Router()
generate_router: Роутер, который будет обрабатывать команды и сообщения, связанные с генерацией username.

Обработчик для команды "Сгенерировать username"
python
Copy
@generate_router.callback_query(F.data == "generate")
async def cmd_generate_username(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Сгенерировать username".
    """
    await query.message.answer("Введите тему/контекст для генерации username:")
    await state.set_state(GenerateUsernameStates.waiting_for_context)
    await query.answer()
@generate_router.callback_query(F.data == "generate"):

Обработчик срабатывает, когда пользователь нажимает кнопку с колбэком generate.

await query.message.answer(...):

Бот отправляет сообщение с запросом ввода контекста.

await state.set_state(GenerateUsernameStates.waiting_for_context):

Бот переходит в состояние waiting_for_context, чтобы ожидать ввода контекста.

await query.answer():

Подтверждает обработку колбэка (убирает "часик" в интерфейсе).

Обработчик для введённого контекста
python
Copy
@generate_router.message(GenerateUsernameStates.waiting_for_context)
async def process_context_input(message: types.Message, bot: Bot, state: FSMContext):
    """
    Обработчик для введённого контекста.
    Генерирует и проверяет username.
    """
    context_text = message.text.strip()
    usernames = await get_available_usernames(bot, context_text, n=3)
    kb = generate_username_kb(usernames)
    await message.answer(
        f"Вот сгенерированные для вас username по теме '{context_text}':",
        reply_markup=kb
    )
    await state.clear()
@generate_router.message(GenerateUsernameStates.waiting_for_context):

Обработчик срабатывает, когда пользователь отправляет сообщение в состоянии waiting_for_context.

context_text = message.text.strip():

Получает текст сообщения (контекст) и удаляет лишние пробелы.

usernames = await get_available_usernames(bot, context_text, n=3):

Вызывает функцию get_available_usernames, которая генерирует и проверяет 3 доступных username.

kb = generate_username_kb(usernames):

Создаёт клавиатуру с сгенерированными username.

await message.answer(...):

Бот отправляет сообщение с результатом и клавиатурой.

await state.clear():

Сбрасывает состояние после завершения.

Как это работает?
Пользователь нажимает кнопку "Сгенерировать username".

Бот переходит в состояние waiting_for_context и запрашивает контекст.

Пользователь вводит контекст (например, "технологии, программирование, AI").

Бот:

Генерирует username через LLM.

Проверяет их доступность.

Выбирает 3 доступных username.

Бот отправляет результат с клавиатурой, где пользователь может выбрать username или запросить новую генерацию.

Пример взаимодействия
Пользователь: Нажимает кнопку "Сгенерировать username".

Бот: "Введите тему/контекст для генерации username:"

Пользователь: "технологии, программирование, AI"

Бот:

Генерирует username: tech_ai, code_master, ai_programmer.

Проверяет их доступность.

Отправляет: "Вот сгенерированные для вас username по теме 'технологии, программирование, AI':"

Кнопки: tech_ai, code_master, ai_programmer, "Сгенерировать ещё", "Назад в главное меню".

Итог
Скрипт handlers/generate.py организует процесс генерации username:

Запрашивает контекст.

Генерирует и проверяет username.

Выводит результат через клавиатуру.

Если остались вопросы или нужно что-то доработать, дайте знать — я помогу! 😊