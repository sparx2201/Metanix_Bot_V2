from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from helper.database import db
from config import Config
import logging

ON = [[InlineKeyboardButton('Upload as Document', callback_data='upload_document_on')],
      [InlineKeyboardButton('Upload as Video', callback_data='upload_video_on')]]


@Client.on_callback_query()
async def set_upload_format(client, query: CallbackQuery):
    logging.info(f"Received callback query: {query}")
    data = query.data
    user_id = query.from_user.id
    logging.info(f"Callback data: {data}, User ID: {user_id}")

    try:
        if data == 'upload_document_on':
            await query.message.delete()
            await db.set_upload_type(user_id, "document")
            await query.message.reply_text("Upload format set to **document**.")
        elif data == 'upload_video_on':
            await query.message.delete()
            await db.set_upload_type(user_id, "video")
            await query.message.reply_text("Upload format set to **video**.")
    except Exception as e:
        logging.error(f"Error processing callback query: {e}")
        await query.message.reply_text("An error occurred while processing your request.")

# Command handler for '/upload'
@Client.on_message(filters.private & filters.command('upload'))
async def handle_upload_settings(client, message: Message):
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    try:
        upload_type = await db.get_upload_type(message.from_user.id)
        logging.info(f"Retrieved upload type: {upload_type} for user ID: {message.from_user.id}")
    except Exception as e:
        await ms.delete()
        await message.reply_text(f"Error: {str(e)}")
        return

    await ms.delete()
    if upload_type == "document":
        await message.reply_text("Your current upload format is set to **Document**.", reply_markup=ON)
    elif upload_type == "video":
        await message.reply_text("Your current upload format is set to **Video**.", reply_markup=ON)
    else:
        await message.reply_text("Please select the upload format:", reply_markup=ON)

from pyrogram import Client, filters
from helper.database import db  # Assuming db is your Database class instance

# REMNAME
@Client.on_message(filters.private & filters.command('document'))
async def upload_document(client, message):
    # Get all the text patterns provided in the command
    SnowDev = await message.reply_text("Please Wait ...")
    user_id = message.from_user.id
    await db.set_upload_type(user_id, "document")
    await SnowDev.edit("**Upload format set to Document ✅**")

@Client.on_message(filters.private & filters.command('video'))
async def upload_video(client, message):
    SnowDev = await message.reply_text("Please Wait ...")
    user_id = message.from_user.id
    await db.set_upload_type(user_id, "video")
    await SnowDev.edit("**Upload format set to Video ✅**")
