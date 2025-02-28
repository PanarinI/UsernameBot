import logging
import asyncio
import re
from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from services.generate import gen_process_and_check
from keyboards.generate import generate_username_kb, error_retry_kb, styles_kb, initial_styles_kb
from keyboards.main_menu import main_menu_kb, back_to_main_kb
from .states import GenerateUsernameStates
import config


generate_router = Router()


### ✅ 1. ОБРАБОТЧИК КНОПКИ "Сгенерировать username"
@generate_router.callback_query(F.data == "generate")
async def cmd_generate_username(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Сгенерировать username".
    """
    logging.info(f"📩 Нажата кнопка 'Сгенерировать username' от {query.from_user.username} (id={query.from_user.id})")

    await state.clear()  # Очищаем состояние перед новой командой
    await asyncio.sleep(0.05)  # ✅ Даем FSM время сброситься

    # Сохраняем время начала генерации в FSM
    await state.update_data(start_time=datetime.now().isoformat())

    await query.message.answer(
        "🔮 О чём должно говорить имя? Опиши тему, и я поймаю три уникальных имени.\n"
        "📖 <i>Например: «загадки истории», «фиолетовые котики», да что угодно</i>",
        parse_mode="HTML",
        reply_markup=back_to_main_kb()
    )

    await state.set_state(GenerateUsernameStates.waiting_for_context)
    await query.answer()  # Telegram требует подтверждения, что callback обработан.


### ✅ 2. ОБРАБОТЧИК КОМАНДЫ /generate
@generate_router.message(Command("generate"))  # Фильтр чтобы /generate срабатывал независимо от состояния
async def cmd_generate_slash(message: types.Message, state: FSMContext):
    """
    Обработчик для команды /generate.
    """
    logging.info(f"📩 Команда /generate от {message.from_user.username} (id={message.from_user.id})")

    await state.clear()  # ⛔️ Принудительно очищаем ВСЕ состояния
    await asyncio.sleep(0.1)  # 🔄 Даём FSM время сброситься

    await message.answer("Введите тему/контекст для генерации username:", reply_markup=back_to_main_kb())
    await state.set_state(GenerateUsernameStates.waiting_for_context)


### ✅ 3. ОБРАБОТЧИК ВВОДА КОНТЕКСТА
@generate_router.message(GenerateUsernameStates.waiting_for_context)
async def process_context_input(message: types.Message, state: FSMContext):
    """
    Обработчик для введённого контекста. Теперь после ввода темы появляется 2 варианта:
    - Без выбора стиля (генерация сразу)
    - Выбрать стиль (открывает второе меню)
    """
    context_text = message.text.strip()
    logging.info(f"📝 Введён контекст: '{context_text}' (от {message.from_user.username}, id={message.from_user.id})")

    # ✅ Проверяем длину контекста
    if len(context_text) > config.MAX_CONTEXT_LENGTH:
        logging.warning(f"⚠️ Контекст слишком длинный ({len(context_text)} символов), обрезаем до {config.MAX_CONTEXT_LENGTH}.")
        await message.answer(f"⚠️ Контекст слишком длинный. Обрезаю до {config.MAX_CONTEXT_LENGTH} символов.")
        context_text = context_text[:config.MAX_CONTEXT_LENGTH]

    # ✅ Сохраняем контекст в FSM, чтобы использовать после выбора стиля
    await state.update_data(context=context_text)

    # ✅ Отправляем inline-клавиатуру с двумя вариантами
    await message.answer(
        "🎭 Как будем искать имя?",
        reply_markup=initial_styles_kb()  # Меню первого уровня
    )

    await state.set_state(GenerateUsernameStates.waiting_for_style)


@generate_router.callback_query(GenerateUsernameStates.waiting_for_style)
async def process_style_choice(query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обрабатывает выбор стиля или генерацию без стиля.
    """
    selected_option = query.data

    if selected_option in ["no_style", "choose_style"]:
        await query.message.edit_text(
            "🎭 Выбери стиль генерации:" if selected_option == "choose_style" else "⏳ Генерация имени...",
            reply_markup=styles_kb() if selected_option == "choose_style" else None
        )

        if selected_option == "no_style":
            # Сохраняем время начала генерации в FSM
            await state.update_data(start_time=datetime.now().isoformat())
            await perform_username_generation(query, state, bot, style=None)
        return

    # Сохраняем время начала генерации перед выбором стиля
    await state.update_data(start_time=datetime.now().isoformat())
    await perform_username_generation(query, state, bot, style=selected_option)


def contains_cyrillic(text: str) -> bool:
    """Проверяет, есть ли в тексте кириллические символы."""
    return bool(re.search(r'[а-яА-Я]', text))


def escape_md(text: str) -> str:
    """Экранирует спецсимволы для MarkdownV2"""
    if not text:
        return ""
    return re.sub(r'([_*[\]()~`>#+-=|{}.!])', r'\\\1', text)

async def send_progress_messages(query: types.CallbackQuery):
    """Фоновая отправка сообщений о процессе генерации."""
    messages = [
        "Выслеживаю...",
        "Прислушиваюсь к цифровому эфиру...",
    ]

    sent_messages = []
    for msg in messages:
        sent_messages.append(await query.message.answer(msg))
        await asyncio.sleep(3)  # Задержка перед следующим сообщением

    return sent_messages  # Список отправленных сообщений

async def start_generation(query: types.CallbackQuery, state: FSMContext, bot: Bot, style: str | None):
    """
    Общая функция генерации username (вызывается и при выборе стиля, и без).
    """
    data = await state.get_data()
    context_text = data.get("context", "")

    if not context_text:
        logging.error("⚠️ Ошибка: Контекст не найден в состоянии!")
        await query.message.answer(
            "❌ Ошибка: не удалось получить тему генерации. Начните заново.",
            reply_markup=main_menu_kb()
        )
        await state.clear()
        return

    logging.info(f"🚀 Запуск генерации username по контексту '{context_text}' и стилю '{style}'")

    # ✅ Отправляем сообщение о начале генерации
    try:
        # 🔄 Отправляем анимированное эмодзи ⏳ (если у пользователя Telegram Premium, оно будет анимированным)
        await query.message.answer("⏳")
        await asyncio.sleep(2)  # Делаем небольшую паузу перед следующим сообщением

        # 📩 Теперь отправляем основное сообщение
        waiting_message = await query.message.answer("Выслеживаю... ")
        await asyncio.sleep(3)  # Делаем небольшую паузу перед следующим сообщением
        waiting_message = await query.message.answer("Прислушиваюсь к цифровому эфиру...")

        logging.info("✅ Сообщение о начале генерации отправлено")
    except Exception as e:
        logging.error(f"❌ Ошибка при отправке сообщения о генерации: {e}")
        return

    # Запускаем отправку сообщений в фоновом режиме
    progress_task = asyncio.create_task(send_progress_messages(query))

    # ✅ Вызываем генерацию
    logging.info("🔄 Вызываем gen_process_and_check()...")

    try:
        raw_usernames = await asyncio.wait_for(
            gen_process_and_check(bot, context_text, style, config.AVAILABLE_USERNAME_COUNT),
            timeout=config.GEN_TIMEOUT
        )

        # Отменяем процесс, если генерация завершилась раньше
        progress_task.cancel()

        logging.info(f"✅ Ответ AI до обработки: {raw_usernames}")

        # 🚨 Проверяем отказ AI (до очистки)
        usernames_cleaned = [u.strip() for u in raw_usernames if u.strip()]  # Убираем пустые строки
        response_text = " ".join(usernames_cleaned).lower()

        # 🚨 Проверяем, что ВЕСЬ СПИСОК username состоит из отказов
        if all(any(phrase in username.lower() for phrase in ["не могу", "противоречит", "извините", "это запрещено", "не допускается"]) for username in usernames_cleaned):
            logging.warning(f"❌ AI отказался генерировать username (контекст: '{context_text}', стиль: '{style}').")
            await query.message.answer(
                "❌ AI отказался генерировать имена по этическим соображениям. Попробуйте изменить запрос.",
                reply_markup=error_retry_kb()
            )
            await state.clear()  # ⛔ Чистим состояние, чтобы не было зацикливания
            return  # ⛔ Выходим


        # ✅ Теперь очищаем список от мусора (пустые строки, пробелы)
        usernames = [u.strip() for u in raw_usernames if u.strip()]

        logging.info(f"✅ список корректно обработан")

    except asyncio.TimeoutError:
        logging.error(f"❌ Ошибка: Время ожидания генерации username истекло (контекст: '{context_text}', стиль: '{style}').")
        await query.message.answer("⏳ Имялов искал имена слишком долго. Попробуйте позже.", reply_markup=main_menu_kb())
        await state.clear()
        return

    logging.info(f"📜 Полученный список usernames: {usernames}")

    # Если список username всё равно пустой, показываем другую ошибку
    if not usernames:
        logging.warning(f"❌ Генерация username не дала результатов (контекст: '{context_text}', стиль: '{style}').")
        await query.message.answer(
            "❌ Не удалось поймать имена. Возможно, тема слишком популярна. Попробуйте чуть изменить запрос или стиль!",
            reply_markup=error_retry_kb()
        )
        return


    kb_usernames = generate_username_kb(usernames)

    # Преобразуем стиль в русское название
    style_rus = config.STYLE_TRANSLATIONS.get(style, style or "")

    # Формируем текст с экранированными символами
    text = f"Вот уникальные имена {'в стиле *' + escape_md(style_rus) + '*' if style else ''} на тему *{escape_md(context_text)}*:"

    await query.message.answer(
        text,
        parse_mode="MarkdownV2",
        reply_markup=kb_usernames
    )

    logging.info("✅ Ответ пользователю отправлен, очищаем состояние")
    await state.clear()

