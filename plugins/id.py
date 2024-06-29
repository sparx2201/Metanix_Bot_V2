from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helper.database import db

# Handle /id command
@Client.on_message(filters.private & filters.command('id'))
async def handle_id_command(client, message):
    user_id = message.from_user.id
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    
    try:
        upload_type = await db.get_upload_type(user_id)
        print(f"Current upload type for user_id={user_id} is {upload_type}")
        await ms.delete()
        
        DOC = InlineKeyboardMarkup([
            [InlineKeyboardButton("Document ✔", callback_data="upload_document_on"), 
             InlineKeyboardButton("Video", callback_data="upload_video_on")],  
            [InlineKeyboardButton("Close", callback_data="close")]
        ])

        VID = InlineKeyboardMarkup([
            [InlineKeyboardButton("Document", callback_data="upload_document_on"), 
             InlineKeyboardButton("Video ✔", callback_data="upload_video_on")],  
            [InlineKeyboardButton("Close", callback_data="close")]
        ])

        if upload_type == "document":
            await message.reply_text(f"Your current upload format: **Document**.", reply_markup=DOC)
            print(f"Reply sent: Current upload format is Document for user_id={user_id}")
        elif upload_type == "video":
            await message.reply_text(f"Your current upload format: **Video**.", reply_markup=VID)
            print(f"Reply sent: Current upload format is Video for user_id={user_id}")
        else:
            print(f"Unknown upload type for user_id={user_id}")
            await message.reply_text("Unknown upload type. Please set your upload type.")
    except Exception as e:
        print(f"Error handling /id command for user_id={user_id}: {e}")
        await message.reply_text("An error occurred. Please try again later.")
    finally:
        await ms.delete()

# Handle callback queries



@Client.on_message(filters.private & filters.command('del'))
async def handle_id_command(client, message):
    
    await db.delete_upload_type(message.from_user.id)
    await message.reply_text("done")
