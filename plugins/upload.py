from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from helper.database import db
from config import Config


# Define the keyboard buttons for upload options
ON = [[InlineKeyboardButton('Upload as Document', callback_data='upload_document_on')]]
OFF = [[InlineKeyboardButton('Upload as Video', callback_data='upload_video_on')]]

@Client.on_message(filters.private & filters.command('upload'))
async def handle_upload_settings(bot: Client, query: CallbackQuery):
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    upload_type = await db.get_upload_type(message.from_user.id)
    await ms.delete()
    if upload_type == "document":
        await message.reply_text(f"Your current upload format is set to **Document**.", reply_markup=InlineKeyboardMarkup(OFF))
    elif upload_type == "video":
        await message.reply_text(f"Your current upload format is set to **Video**.", reply_markup=InlineKeyboardMarkup(ON))
    else:
        await message.reply_text("Please select the upload format:", reply_markup=InlineKeyboardMarkup(ON))

@Client.on_callback_query(filters.regex('(upload_document_on|upload_video_on)'))
async def set_upload_format(bot: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    print("Received callback query for:", data)
    print("User ID:", user_id)

    if data == 'upload_document_on':
        await db.set_upload_type(user_id, "document")
        new_upload_type = await db.get_upload_type(user_id)
        print("New upload type:", new_upload_type)
        await query.message.edit(f"Upload format set to **{new_upload_type.capitalize()}**.", reply_markup=InlineKeyboardMarkup(OFF))
    elif data == 'upload_video_on':
        await db.set_upload_type(user_id, "video")
        new_upload_type = await db.get_upload_type(user_id)
        print("New upload type:", new_upload_type)
        await query.message.edit(f"Upload format set to **{new_upload_type.capitalize()}**.", reply_markup=InlineKeyboardMarkup(ON))
