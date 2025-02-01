# UsernameBot
A bot to generate, check available and register bright Telegram usernames



/telegram_bot_project
│── main.py                 # Запуск бота
│── config.py               # Конфигурация (токен, настройки)
│── bot_setup.py            # Инициализация бота и диспетчера
│── handlers/               # Основная логика бота (обработчики команд и callback-кнопок)
│   ├── start.py            # Обработчик /start и меню
│   ├── generate.py         # Генерация username
│   ├── check.py            # Проверка доступности username
│   ├── register.py         # (если реализуем) регистрация username
│   ├── inline.py           # Inline-режим (если понадобится)
│── services/               # Бизнес-логика (чистые функции)
│   ├── username_generator.py  # Генерация username через AI API
│   ├── availability_checker.py  # Проверка username через API Telegram
│   ├── username_register.py  # Логика регистрации (если возможно)
│── keyboards/              # Разные inline-клавиатуры
│   ├── menu.py             # Главное меню
│   ├── generate.py         # Клавиатура генерации username
│   ├── register.py         # Кнопки для подтверждения регистрации
│── utils/                  # Вспомогательные функции
│   ├── logger.py           # Логирование
│   ├── helpers.py          # Разные утилиты
│── requirements.txt        # Список зависимостей (aiogram, requests и т. д.)
│── .env                    # Хранение токенов (если используем dotenv)
│── README.md               # Документация проекта


📌 Описание модулей

Четкое разделение обработчиков (handlers) и бизнес-логики (services)
Бот получает команды из handlers/
Логика работы username-генерации из services/
Все клавиатуры хранятся в keyboards/ (чтобы не смешивать с логикой)
Вспомогательные функции в utils/
