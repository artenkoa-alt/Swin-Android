
import os
import sqlite3
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = {
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
}

if not TOKEN:
    raise RuntimeError("BOT_TOKEN не задан")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

db = sqlite3.connect("devices.db")
db.execute("""
CREATE TABLE IF NOT EXISTS devices (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    approved INTEGER DEFAULT 0
)
""")
db.commit()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 <b>Swin-Android</b>\n\n"
        "Бот удалённой поддержки.\n"
        "Команды:\n"
        "/register — зарегистрировать устройство\n"
        "/status — проверить регистрацию\n"
        "/help — помощь"
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "/register — добровольная регистрация\n"
        "/status — состояние регистрации\n"
        "/devices — список зарегистрированных устройств (админ)\n"
        "/request ID — запросить согласие пользователя (админ)"
    )


@dp.message(Command("register"))
async def register(message: Message):
    user = message.from_user
    db.execute(
        "INSERT OR REPLACE INTO devices "
        "(user_id, username, approved) VALUES (?, ?, 0)",
        (user.id, user.username or user.full_name)
    )
    db.commit()

    await message.answer(
        "✅ Ты зарегистрирован в Swin-Android.\n"
        "Регистрация не даёт никому доступ к твоему телефону."
    )


@dp.message(Command("status"))
async def status(message: Message):
    result = db.execute(
        "SELECT approved FROM devices WHERE user_id = ?",
        (message.from_user.id,)
    ).fetchone()

    if result is None:
        await message.answer("Устройство не зарегистрировано. Напиши /register.")
    else:
        await message.answer(
            "Регистрация активна.\n"
            "Удалённый сеанс: " +
            ("разрешён" if result[0] else "не активен")
        )


@dp.message(Command("devices"))
async def devices(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет доступа.")
        return

    rows = db.execute(
        "SELECT user_id, username, approved FROM devices"
    ).fetchall()

    if not rows:
        await message.answer("Пока нет зарегистрированных устройств.")
        return

    text = "<b>Зарегистрированные пользователи:</b>\n\n"
    for user_id, username, approved in rows:
        text += (
            f"ID: <code>{user_id}</code>\n"
            f"Имя: {username}\n"
            f"Сеанс: {'разрешён' if approved else 'не активен'}\n\n"
        )

    await message.answer(text)


@dp.message(Command("request"))
async def request_access(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет доступа.")
        return

    parts = (message.text or "").split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /request ID")
        return

    user_id = int(parts[1])
    result = db.execute(
        "SELECT user_id FROM devices WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if not result:
        await message.answer("Пользователь не зарегистрирован.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Разрешить запрос",
            callback_data=f"consent:yes:{user_id}"
        ),
        InlineKeyboardButton(
            text="Отклонить",
            callback_data=f"consent:no:{user_id}"
        )
    ]])

    try:
        await bot.send_message(
            user_id,
            "🔐 Администратор запрашивает сеанс поддержки.\n"
            "Это пока только запрос. Никакой доступ не предоставлен.",
            reply_markup=keyboard
        )
        await message.answer("Запрос отправлен пользователю.")
    except Exception:
        await message.answer("Не удалось отправить запрос. Пользователь должен открыть бота через /start.")


@dp.callback_query(F.data.startswith("consent:"))
async def consent(callback: CallbackQuery):
    _, choice, target = callback.data.split(":")
    if int(target) != callback.from_user.id:
        await callback.answer("Это не твой запрос.", show_alert=True)
        return

    if choice == "yes":
        await callback.message.edit_text(
            "✅ Запрос принят. Для доступа к экрану потребуется "
            "отдельное системное разрешение Android."
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"Пользователь {callback.from_user.id} согласился на запрос."
                )
            except Exception:
                pass
    else:
        await callback.message.edit_text("❌ Запрос отклонён.")

    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
