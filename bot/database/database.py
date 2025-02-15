import asyncpg
import os
import logging
import sys
import config
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Загружаем переменные окружения из .env (ТОЛЬКО для локального режима)
IS_LOCAL = os.getenv("LOCAL_RUN", "false").lower() == "true"

# Принудительно загружаем переменные (вдруг Амвера игнорит?)
load_dotenv()

logging.debug("🔍 DEBUG: Проверяем переменные окружения...")
print("DEBUG: Проверяем переменные окружения")
print(f"ENV HOST: {os.getenv('HOST') or '❌ НЕ НАЙДЕН'}")
print(f"ENV DATABASE: {os.getenv('DTBS') or '❌ НЕ НАЙДЕН'}")
print(f"ENV USER: {os.getenv('USER') or '❌ НЕ НАЙДЕН'}")
print(f"ENV PASSWORD: {'✅' if os.getenv('PSWRD') else '❌ НЕ НАЙДЕНА'}")

# Загружаем переменные окружения из Amvera
DB_CONFIG = {
    "database": os.getenv("DTBS") or "❌ НЕ НАЙДЕНА",
    "user": os.getenv("USER") or "❌ НЕ НАЙДЕН",
    "password": os.getenv("PSWRD") or "❌ НЕ НАЙДЕНА",
    "host": os.getenv("HOST") or "❌ НЕ НАЙДЕН",
    "port": os.getenv("PORT", "5432"),  # По умолчанию 5432
}

logging.info(f"🔍 Используется база данных: {'ЛОКАЛЬНАЯ' if IS_LOCAL else 'АМВЕРА'}")
logging.info(f"    HOST = {DB_CONFIG['host']}")
logging.info(f"    DB NAME = {DB_CONFIG['database']}")
logging.info(f"    USER = {DB_CONFIG['user']}")
logging.info(f"    PASSWORD = {'✅' if DB_CONFIG['password'] else '❌ НЕ НАЙДЕНА'}")


sys.stderr.write("🔥🔥🔥 DEBUG: ЭТО ДОЛЖНО ПОКАЗАТЬСЯ В ЛОГЕ! 🔥🔥🔥\n")
sys.stderr.flush()

print("DEBUG: Подключение к базе данных")
print(f"HOST: {DB_CONFIG['host']}")
print(f"DB NAME: {DB_CONFIG['database']}")
print(f"USER: {DB_CONFIG['user']}")
print(f"PASSWORD: {'✅' if DB_CONFIG['password'] else '❌ НЕ НАЙДЕНА'}")

# Проверяем наличие SQL-файлов перед загрузкой
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREATE_TABLE_SQL_PATH = os.path.join(BASE_DIR, "create_table.sql")
INSERT_SQL_PATH = os.path.join(BASE_DIR, "insert_username.sql")

if not os.path.exists(CREATE_TABLE_SQL_PATH):
    logging.error(f"❌ Файл {CREATE_TABLE_SQL_PATH} не найден!")

if not os.path.exists(INSERT_SQL_PATH):
    logging.error(f"❌ Файл {INSERT_SQL_PATH} не найден!")

# Загружаем SQL-запросы из файлов
INSERT_SQL = None
if os.path.exists(INSERT_SQL_PATH):
    with open(INSERT_SQL_PATH, "r", encoding="utf-8") as file:
        INSERT_SQL = file.read()

# Глобальный пул соединений
pool = None

async def init_db_pool():
    """Создаёт пул соединений к БД при запуске приложения."""
    global pool
    try:
        pool = await asyncpg.create_pool(**DB_CONFIG)
        logging.info("✅ Пул соединений к БД создан.")
    except Exception as e:
        logging.error(f"❌ Ошибка при создании пула соединений: {e}")

async def get_connection():
    """Получает соединение из пула."""
    global pool
    if not pool:  # Если пул не создан, создаём его
        await init_db_pool()
    return await pool.acquire()  # Берём соединение из пула

async def close_db_pool():
    """Закрывает пул соединений при завершении работы."""
    global pool
    if pool:
        await pool.close()
        logging.info("✅ Пул соединений закрыт.")

async def init_db():
    """Создаёт таблицу, если её нет."""
    await init_db_pool()  # Инициализируем пул, если он не создан
    conn = await get_connection()
    try:
        if os.path.exists(CREATE_TABLE_SQL_PATH):
            with open(CREATE_TABLE_SQL_PATH, "r", encoding="utf-8") as file:
                create_table = file.read()  # Читаем SQL из файла

            await conn.execute(create_table)  # Выполняем SQL в БД
            logging.info("✅ Таблица 'generated_usernames' проверена/создана.")
        else:
            logging.error(f"❌ Файл {CREATE_TABLE_SQL_PATH} не найден! Таблица не будет создана.")
    except Exception as e:
        logging.error(f"❌ Ошибка при создании таблицы: {e}")
    finally:
        await pool.release(conn)  # Освобождаем соединение

async def save_username_to_db(username: str, status: str, context: str, category: str, llm: str):
    """Сохраняет username в базу данных."""
    if len(context) > config.MAX_CONTEXT_LENGTH:
        logging.warning(
            f"⚠️ Контекст слишком длинный ({len(context)} символов), обрезаем до {config.MAX_CONTEXT_LENGTH}."
        )
        context = context[:config.MAX_CONTEXT_LENGTH]  # Обрезаем строку до нужной длины

    conn = await get_connection()
    try:
        if INSERT_SQL:
            await conn.execute(INSERT_SQL, username, status, category, context, llm)
            log_message = f"✅ Добавлен в БД: @{username} | {status} | {category} | {context} | {llm}"
            logging.info(log_message)
            print(log_message)
        else:
            logging.error("❌ INSERT_SQL не загружен! Файл insert_username.sql отсутствует.")
    except Exception as e:
        logging.error(f"❌ Ошибка при сохранении в БД: {e}")
    finally:
        await pool.release(conn)  # Освобождаем соединение
