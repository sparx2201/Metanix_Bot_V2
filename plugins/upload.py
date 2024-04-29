from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from helper.database import db
from config import Config

# Define the keyboard buttons for upload options
UPLOAD_OPTIONS = [
    [InlineKeyboardButton('📁 Upload Document', callback_data='upload_document')],
    [InlineKeyboardButton('🎥 Upload Video', callback_data='upload_video')],
]

# Handle the upload command to choose between document and video uploads
@Client.on_message(filters.private & filters.command('upload'))
async def handle_upload_command(bot, message):
    await message.reply_text("Please select the upload type:", reply_markup=InlineKeyboardMarkup(UPLOAD_OPTIONS))

# Handle the callback data for upload options
@Client.on_callback_query(filters.regex(r"upload_(document|video)"))
async def handle_upload_buttons(bot, update):
    file_type = update.data.split('_')[1]
    await db.set_upload_type(update.from_user.id, file_type)
    await update.answer("Upload type selected successfully.")

# Handle file uploads
@Client.on_message(filters.private & (filters.document | filters.video))
async def handle_file_upload(bot, message):
    user_id = message.from_user.id
    upload_type = await db.get_upload_type(user_id)
    if upload_type == "document":
        await message.reply_text("You have selected to upload as a document.")
    elif upload_type == "video":
        await message.reply_text("You have selected to upload as a video.")


