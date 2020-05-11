import discord
from discord.ext import commands
from cogs.slothcurrency import SlothCurrency
from mysqldb2 import *

class ReactionRoles(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_ready(self):
        print("ReactionRoles cog is online!")
        await SlothCurrency.text_download_update(self.client)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, overload):
        guild = self.client.get_guild(overload.guild_id)
        user = discord.utils.get(guild.members, id=overload.user_id)

        if user.bot:
            return

        # Language rooms
        language_rooms = [695491104417513552, 683987207065042944, 688037387561205824]


        if not overload.channel_id in language_rooms:
            return

        message_texts = await self.get_message_texts(overload.message_id, overload.emoji)
        if message_texts:
            with open(f"texts/{message_texts[0][2]}/{message_texts[0][3]}", 'r', encoding='utf-8') as f:
                text = f.readlines()
                text = ''.join(text)
            embed = discord.Embed(title='', description=text, colour=discord.Colour.dark_green())
            embed.set_footer(text=f"Guild name: {guild.name}")
            embed.set_author(name=user, icon_url=user.avatar_url)
            return await user.send(embed=embed)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def register_text(self, ctx, mid: discord.Message = None, react: str = None, category: str = None, file_name: str = None):
        await ctx.message.delete()
        if not mid:
            return await ctx.send("**Inform a message ID!**", delete_after=3)
        elif not react:
            return await ctx.send("**Inform a reaction!**", delete_after=3)
        elif not category:
            return await ctx.send("**Inform a category!**", delete_after=3)
        elif not file_name:
            return await ctx.send("**Inform the file name!**", delete_after=3)

        await self.insert_registered_text(mid.id, react, category.lower(), file_name)
        await mid.add_reaction(react)
        return await ctx.send(f"**File `{file_name}` successfully registered!**", delete_after=3)

    # Table UserCurrency
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_table_registered_text(self, ctx):
        await ctx.message.delete()
        mycursor, db = await the_data_base3()
        await mycursor.execute(
            "CREATE TABLE RegisteredText (message_id bigint, reaction VARCHAR(50), category VARCHAR(20), file_name VARCHAR(50))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *RegisteredText* created!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def drop_table_registered_text(self, ctx):
        await ctx.message.delete()
        mycursor, db = await the_data_base3()
        await mycursor.execute("DROP TABLE RegisteredText")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *RegisteredText* dropped!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_table_registered_text(self, ctx):
        await ctx.message.delete()
        mycursor, db = await the_data_base3()
        await mycursor.execute("DROP TABLE RegisteredText")
        await db.commit()
        await mycursor.execute(
            "CREATE TABLE RegisteredText (message_id bigint, reaction VARCHAR(50), category VARCHAR(20), file_name VARCHAR(50))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *RegisteredText* reseted!**", delete_after=3)


    async def insert_registered_text(self, mid: int, react, category: str, file_name: str):
        mycursor, db = await the_data_base3()
        await mycursor.execute("INSERT INTO RegisteredText (message_id, reaction, category, file_name) VALUES (%s, %s, %s, %s)", (mid, react, category, file_name))
        await db.commit()
        await mycursor.close()

    async def remove_specific_image_texts(self, mid: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"DELETE FROM RegisteredText WHERE message_id = {mid}")
        await db.commit()
        await mycursor.close()

    async def there_are_texts(self, mid: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"SELECT * FROM RegisteredText WHERE message_id = {mid}")
        texts = await mycursor.fetchall()
        await mycursor.close()
        if len(texts) > 0:
            return True
        else:
            return False

    async def get_message_texts(self, mid: int, reaction):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"SELECT * FROM RegisteredText WHERE message_id = {mid} and reaction = {reaction}")
        texts = await mycursor.fetchall()
        await mycursor.close()
        return texts

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear_image_texts(self, ctx, mid: discord.Message = None):
        await ctx.message.delete()
        if not mid:
            return await ctx.send("**Inform a message ID to clear!**", delete_after=3)

        if await self.there_are_texts(mid.id):
            await self.remove_specific_image_texts(mid.id)
            return await ctx.send(f"**All texts from the message/image with the ID: {mid.id} were deleted!**", delete_after=5)
        else:
            return await ctx.send(f"**There are no texts in the message/image with the ID: {mid.id}**", delete_after=5)


def setup(client):
    client.add_cog(ReactionRoles(client))