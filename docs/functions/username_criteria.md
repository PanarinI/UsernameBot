🔹 Полный список критериев для допустимого username в Telegram
Если пользователь вводит некорректное имя (например, кириллицу), бот должен вывести все правила.

✅ Критерии Telegram для username:

🔹 Только латинские буквы (A-Z, a-z), цифры (0-9) и подчёркивание (_).
🔹 Минимальная длина: 5 символов.
🔹 Максимальная длина: 32 символа.
🔹 Не может начинаться и заканчиваться _ (подчёркиванием).
🔹 Не может содержать два подряд идущих _ (например, hello__world).






client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

response = client.chat.completions.create(
    model="gemini-flash-1.5-8b",
    messages=[
        {"role": "system", "content": "You are a talking dog. Greet me Woof!"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)

gemini-flash-1.5-8b"