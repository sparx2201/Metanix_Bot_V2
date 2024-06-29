from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper.database import db

# Handle /id command
@Client.on_message(filters.private & filters.command('id'))
async def handle_id_command(client, message):
    user_id = message.from_user.id
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    upload_type = await db.get_upload_type(message.from_user.id)
    print(f"Current upload type for user_id={message.from_user.id} is {upload_type}")
    await ms.delete()

    ON = InlineKeyboardMarkup([
    [InlineKeyboardButton("Set to Document", callback_data="upload_document_on")],
    [InlineKeyboardButton("Set to Video", callback_data="upload_video_on")]
])

    if upload_type == "document":
        await message.reply_text(f"Your current upload format is set to **Document**.", reply_markup=ON)
        print(f"Reply sent: Current upload format is Document for user_id={message.from_user.id}")
    elif upload_type == "video":
        await message.reply_text(f"Your current upload format is set to **Video**.", reply_markup=ON)
        print(f"Reply sent: Current upload format is Video for user_id={message.from_user.id}")
    else:
        await message.reply_text("Please select the upload format:", reply_markup=ON)
        print(f"Reply sent: User needs to select upload format for user_id={message.from_user.id}")
        
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

    if data == "upload_document_on":
        await query.message.reply_text("Upload format set to **document**.")
        print(f"User ID {user_id} sent in response to callback query")
