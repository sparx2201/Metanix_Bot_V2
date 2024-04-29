from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from helper.database import db

ON = [[InlineKeyboardButton('Upload as Document', callback_data='upload_document_on')]]
OFF = [[InlineKeyboardButton('Upload as Video', callback_data='upload_video_on')]]



@Client.on_message(filters.private & filters.command('upload'))
async def handle_upload_settings(bot: Client, message: Message):
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.message_id)
    upload_type = await db.get_upload_type(message.from_user.id)
    await ms.delete()
    if upload_type == "document":
        await message.reply_text(f"Your current upload format is set to **Document**.", reply_markup=InlineKeyboardMarkup(ON))
    elif upload_type == "video":
        await message.reply_text(f"Your current upload format is set to **Video**.", reply_markup=InlineKeyboardMarkup(OFF))
    else:
        await message.reply_text("Please select the upload format:", reply_markup=InlineKeyboardMarkup(ON))

@Client.on_callback_query(filters.regex('(upload_document_on|upload_video_on|upload_document_off|upload_video_off)'))
async def set_upload_format(bot: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    if data == 'upload_document_on':
        await db.set_upload_type(user_id, "document")
        await query.message.edit("Upload format set to **Document**.", reply_markup=InlineKeyboardMarkup(ON))
    elif data == 'upload_video_on':
        await db.set_upload_type(user_id, "video")
        await query.message.edit("Upload format set to **Video**.", reply_markup=InlineKeyboardMarkup(OFF))

@app.on_message(filters.private & (filters.document | filters.video))
async def handle_media(bot: Client, message: Message):
    upload_type = await db.get_upload_type(message.from_user.id)
    ms = await message.reply_text(f"Trying to upload as {upload_type}...")
    if upload_type == "document" and message.document:
        await ms.edit(f"Uploading document: {message.document.file_name}")
        # Implement your document upload logic here
    elif upload_type == "video" and message.video:
        await ms.edit(f"Uploading video: {message.video.file_name}")
        # Implement your video upload logic here
    else:
        await ms.edit("Invalid upload format or media type.")


