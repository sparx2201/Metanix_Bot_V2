from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from helper.database import db
from config import Config


# Define the keyboard buttons for upload options
ON = [[InlineKeyboardButton('Upload as Document', callback_data='upload_video_on')]]
OFF = [[InlineKeyboardButton('Upload as Video', callback_data='upload_document_on')]]

@Client.on_message(filters.private & filters.command('upload'))
async def handle_upload_settings(bot, message):
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    upload_type = await db.get_upload_type(message.from_user.id)
    await ms.delete()
    if upload_type == "document":
        await message.reply_text(f"Your current upload format is set to **Document**.", reply_markup=InlineKeyboardMarkup(ON))
    elif upload_type == "video":
        await message.reply_text(f"Your current upload format is set to **Video**.", reply_markup=InlineKeyboardMarkup(OFF))
    else:
        await message.reply_text("Please select the upload format:", reply_markup=InlineKeyboardMarkup(ON))

@Client.on_callback_query(filters.regex(r'upload_(document|video)_(on|off)'))
async def set_upload_format(bot, query):
    data = query.data
    user_id = query.from_user.id

    format_type, status = data.split("_")[1:]  # Extract format type and status from the callback data

    if status == 'on':
        await db.set_upload_type(user_id, format_type)
        if format_type == 'document':
            await query.message.edit("Upload format set to **Document**.", reply_markup=InlineKeyboardMarkup(ON))
        elif format_type == 'video':
            await query.message.edit("Upload format set to **Video**.", reply_markup=InlineKeyboardMarkup(OFF))
    elif status == 'off':
        # Handle off status if needed
        pass
