from pyrogram import Client, filters
from helper.database import db  # Assuming db is your Database class instance


# REMNAME
@Client.on_message(filters.private & filters.command('set_remname'))
async def add_remname(client, message):
    if len(message.command) == 1:
        return await message.reply_text("**__Give The Remname Text__\n\nExample:- `/set_remname text_pattern1, text_pattern2, ...`**")
    
    # Get all the text patterns provided in the command
    remname_text = message.text.split(' ', 1)[1]
    remname_patterns = [pattern.strip() for pattern in remname_text.split(',')]
    
    SnowDev = await message.reply_text("Please Wait ...")
    for pattern in remname_patterns:
        await db.set_remname(message.from_user.id, pattern)
    
    await SnowDev.edit("**Remname Text Saved Successfully ✅**")

@Client.on_message(filters.private & filters.command('del_remname'))
async def delete_remname(client, message):
    SnowDev = await message.reply_text("Please Wait ...")
    await db.delete_remname(message.from_user.id)
    await SnowDev.edit("**Remname Text Deleted Successfully 🗑️**")

@Client.on_message(filters.private & filters.command('see_remname'))
async def see_remname(client, message):
    SnowDev = await message.reply_text("Please Wait ...")
    remname_text = await db.get_remname(message.from_user.id)
    if remname_text:
        await SnowDev.edit(f"**Your Remname Texts:-**\n\n{remname_text}")
    else:
        await SnowDev.edit("**You Don't Have Any Remname Texts ❌**")

