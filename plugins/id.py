from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton



CHECK_ID_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("Check ID", callback_data="check_id")]
])

# Handle /id command
@Client.on_message(filters.private & filters.command('id'))
async def handle_id_command(client, message):
    user_id = message.from_user.id
    print(f"ID command received from user_id={user_id}")
    await message.reply_text(
        "Press the button below to check your ID:",
        reply_markup=CHECK_ID_KEYBOARD
    )

# Handle callback queries
@Client.on_callback_query()
async def handle_callback_query(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    print(f"Callback query received: data={data}, user_id={user_id}")

    if data == "check_id":
        await query.message.reply_text(f"Your user ID is: {user_id}")
        print(f"User ID {user_id} sent in response to callback query")
