
import os
import sqlite3
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
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
    TOKEN,
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

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Мои устройства")],
        [KeyboardButton(text="🟢 Статус устройств")],
        [KeyboardButton(text="🔐 Запрос подключения")],
        [KeyboardButton(text="📺 Запрос демонстрации")],
        [KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🔥 <b>SWIN-ANDROID</b>\n\n"
        "Панель удалённой поддержки.\n"
        "Выбери действие в меню.",
        reply_markup=menu
    )


@dp.message(Command("register"))
async def register(message: Message):
    user = message.from_user

    db.execute(
        "INSERT OR IGNORE INTO devices "
        "(user_id, username, approved) VALUES (?, ?, 0)",
        (user.id, user.username or user.full_name)
    )
    db.commit()

    await message.answer(
        "✅ Устройство зарегистрировано.\n"
        "Регистрация не предоставляет удалённого доступа.",
        reply_markup=menu
    )


@dp.message(F.text == "📱 Мои устройства")
@dp.message(Command("devices"))
async def devices(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Эта функция доступна администратору.")
        return

    rows = db.execute(
        "SELECT user_id, username FROM devices ORDER BY user_id"
    ).fetchall()

    if not rows:
        await message.answer("Устройств пока нет.")
        return

    text = "<b>📱 Зарегистрированные устройства</b>\n\n"

    for user_id, username in rows:
        text += (
            f"👤 {username}\n"
            f"ID: <code>{user_id}</code>\n\n"
        )

    await message.answer(text)


@dp.message(F.text == "🟢 Статус устройств")
@dp.message(Command("status"))
async def status(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет доступа.")
        return

    count = db.execute(
        "SELECT COUNT(*) FROM devices"
    ).fetchone()[0]

    await message.answer(
        f"🟢 Бот работает\n"
        f"📱 Зарегистрировано устройств: {count}\n"
        f"🔐 Активных сеансов: 0"
    )


async def send_request(message: Message, kind: str):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет доступа.")
        return

    parts = (message.text or "").split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer(
            "Укажи ID пользователя:\n"
            f"/{'request' if kind == 'connection' else 'screen'} ID"
        )
        return

    user_id = int(parts[1])

    exists = db.execute(
        "SELECT user_id FROM devices WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if not exists:
        await message.answer("Устройство не зарегистрировано.")
        return

    label = (
        "подключение для поддержки"
        if kind == "connection"
        else "демонстрацию экрана"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Разрешить",
            callback_data=f"consent:yes:{kind}"
        ),
        InlineKeyboardButton(
            text="❌ Отклонить",
            callback_data=f"consent:no:{kind}"
        )
    ]])

    try:
        await bot.send_message(
            user_id,
            f"🔐 Запрос администратора: {label}.\n"
            "Доступ будет предоставлен только после твоего согласия.",
            reply_markup=keyboard
        )
        await message.answer("✅ Запрос отправлен.")
    except Exception:
        await message.answer(
            "Не удалось отправить запрос. "
            "Пользователь должен открыть бота через /start."
        )


@dp.message(Command("request"))
async def request(message: Message):
    await send_request(message, "connection")


@dp.message(Command("screen"))
async def screen(message: Message):
    await send_request(message, "screen")


@dp.callback_query(F.data.startswith("consent:"))
async def consent(callback: CallbackQuery):
    _, choice, kind = callback.data.split(":")

    if choice == "yes":
        text = (
            "✅ Ты согласился на запрос.\n"
            "Для реального подключения потребуется "
            "отдельное подтверждение в Android-приложении."
        )
    else:
        text = "❌ Запрос отклонён."

    await callback.message.edit_text(text)

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"Пользователь {callback.from_user.id}: "
                f"{'согласился' if choice == 'yes' else 'отклонил'} "
                f"запрос {kind}."
            )
        except Exception:
            pass

    await callback.answer()


@dp.message(F.text == "🔐 Запрос подключения")
async def connection_help(message: Message):
    await message.answer("Команда администратора:\n/request ID")


@dp.message(F.text == "📺 Запрос демонстрации")
async def screen_help(message: Message):
    await message.answer("Команда администратора:\n/screen ID")


@dp.message(F.text == "❓ Помощь")
@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "<b>Команды Swin-Android</b>\n\n"
        "/start — меню\n"
        "/register — регистрация\n"
        "/devices — список устройств\n"
        "/status — состояние\n"
        "/request ID — запрос подключения\n"
        "/screen ID — запрос демонстрации экрана"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
