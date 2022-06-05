""" global banned and un-global banned module """

import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from driver.filters import command
from driver.decorators import sudo_users_only
from driver.database.dbchat import get_served_chats
from driver.database.dbpunish import add_gban_user, is_gbanned_user, remove_gban_user

from config import BOT_NAME, SUDO_USERS, BOT_USERNAME as bn


@Client.on_message(command(["gban", f"gban@{bn}"]) & ~filters.edited)
@sudo_users_only
async def global_banned(c: Client, message: Message):
    if not message.reply_to_message:
        if len(message.command) < 2:
            await message.reply_text("**İstifadə:**\n\n/gban [İstifadəçi adı | İstifadəçi id]")
            return
        user = message.text.split(None, 2)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await c.get_users(user)
        from_user = message.from_user
        BOT_ID = await c.get_me()
        if user.id == from_user.id:
            return await message.reply_text(
                "You can't gban yourself !"
            )
        elif user.id == BOT_ID:
            await message.reply_text("Özümü gban niyə edim?🙄🤦🏻")
        elif user.id in SUDO_USERS:
            await message.reply_text("sudo istifadəçini gban edə bilməzsən!")
        else:
            await add_gban_user(user.id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(
                f"🚷 **qlobal qadağa {user.mention}**\n⏱ gözləyən zaman: `{len(served_chats)}`"
            )
            number_of_chats = 0
            for num in served_chats:
                try:
                    await c.ban_chat_member(num, user.id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
🚷 **Yeni qlobal qadağa [{BOT_NAME}](https://t.me/{bn})

**origin:** {message.chat.title} [`{message.chat.id}`]
**Sudo İstifadəçi:** {from_user.mention}
**Banned İstifadəçi:** {user.mention}
**Banned İstifadəçi ID:** `{user.id}`
**Söhbətlər:** `{number_of_chats}`"""
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(
                f"{ban_text}",
                disable_web_page_preview=True,
            )
        return
    from_user_id = message.from_user.id
    from_user_mention = message.from_user.mention
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    BOT_ID = await c.get_me()
    if user_id == from_user_id:
        await message.reply_text("Sən özünü gban edə bilməzsən!")
    elif user_id == BOT_ID:
        await message.reply_text("özümü gban edə bilmərəm!")
    elif user_id in SUDO_USERS:
        await message.reply_text("sudo istifadəçini gban edə bilməzsən!")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if is_gbanned:
            await message.reply_text("Bu istifadəçi artıq gbandır!")
        else:
            await add_gban_user(user_id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(
                f"🚷 **qlobal qadağa {mention}**\n⏱ gözləyən zaman: `{len(served_chats)}`"
            )
            number_of_chats = 0
            for num in served_chats:
                try:
                    await c.ban_chat_member(num, user_id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
🚷 **Yeni qlobal qadağa [{BOT_NAME}](https://t.me/{bn})

**Origin:** {message.chat.title} [`{message.chat.id}`]
**Sudo İstifadəçi:** {from_user_mention}
**Banned İstifadəçi:** {mention}
**Banned İstifadəçi ID:** `{user_id}`
**Söhbətlər:** `{number_of_chats}`"""
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(
                f"{ban_text}",
                disable_web_page_preview=True,
            )
            return


@Client.on_message(command(["ungban", f"ungban@{bn}"]) & ~filters.edited)
@sudo_users_only
async def ungban_global(c: Client, message: Message):
    chat_id = message.chat.id
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "**kullanım:**\n\n/ungban [İstifadəçi adı | İstifadəçi id]"
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await c.get_users(user)
        from_user = message.from_user
        BOT_ID = await c.get_me()
        if user.id == from_user.id:
            await message.reply_text("Özünüzə qadağa qoya bilməzsiniz, çünki sizə qadağa qoyula bilməz!")
        elif user.id == BOT_ID:
            await message.reply_text("Özümə qadağa qoya bilmərəm, çünki gban ola bilmirəm!")
        elif user.id in SUDO_USERS:
            await message.reply_text("Sudo istifadəçiləri gbanlı/gbansız ola bilməz!")
        else:
            is_gbanned = await is_gbanned_user(user.id)
            if not is_gbanned:
                await message.reply_text("Bu istifadəçinin qadağası açılmadı!")
            else:
                await c.unban_chat_member(chat_id, user.id)
                await remove_gban_user(user.id)
                await message.reply_text("✅ Bu istifadəçinin qadağası açıldı")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    BOT_ID = await c.get_me()
    if user_id == from_user_id:
        await message.reply_text("Özünüzə qadağa qoya bilməzsiniz, çünki sizə qadağa qoyula bilməz!")
    elif user_id == BOT_ID:
        await message.reply_text(
            "Özümə qadağa qoya bilmərəm, çünki gban ola bilmirəm!"
        )
    elif user_id in SUDO_USERS:
        await message.reply_text("Sudo istifadəçilər bloklana bilməz/ungbanned !")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if not is_gbanned:
            await message.reply_text("Bu istifadəçi gban deyil!")
        else:
            await c.unban_chat_member(chat_id, user_id)
            await remove_gban_user(user_id)
            await message.reply_text("✅ Bu istifadəçinin qadağası açıldı")
