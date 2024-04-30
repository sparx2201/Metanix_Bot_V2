from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from helper.database import db
from config import Config

# Define the keyboard buttons for upload options
ON = [[InlineKeyboardButton('Upload as Document', callback_data='upload_document_on')],
      [InlineKeyboardButton('Upload as Video', callback_data='upload_video_on')]]

@Client.on_message(filters.private & filters.command('upload'))
async def handle_upload_settings(client, message):
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    upload_type = await db.get_upload_type(message.from_user.id)
    await ms.delete()
    if upload_type == "document":
        await message.reply_text(f"Your current upload format is set to **Document**.", reply_markup=InlineKeyboardMarkup(ON))
    elif upload_type == "video":
        await message.reply_text(f"Your current upload format is set to **Video**.", reply_markup=InlineKeyboardMarkup(ON))
    else:
        await message.reply_text("Please select the upload format:", reply_markup=InlineKeyboardMarkup(ON))

@Client.on_callback_query(filters.regex('.*?(upload_document_on|upload_video_on).*?'))
async def set_upload_format(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    if data == 'upload_document_on':
        await query.message.delete()
        #await db.set_upload_type(user_id, "document")
        #await bot.send_message("Upload format set to **document**.")
   
    elif data == 'upload_video_on':
        await query.message.delete()
       # await db.set_upload_type(user_id, "video")
      #  await bot.send_message("Upload format set to **video**.")
      

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
