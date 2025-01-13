from discord.ext import commands
from src.controller.util_service import Category
import re

class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(name="Contact", help="Sendet Nachricht an eine Person", usage=Category.settings)
    async def contact(self, ctx, *, arg):
        regex=r"\d{18}"
        match = re.search(regex, arg)
        if match:
            user_id = match.group()
            user = await self.client.fetch_user(user_id)
            if user:
                await user.send(re.sub(regex, "", arg))
                await ctx.send(f"Nachricht gesendet an: {user_id}")
            else:
                await ctx.send("Fehler beim senden, sorry ;(")


    @commands.command(name="help", help="Bessere version von help", usage=Category.settings)
    async def help(self, ctx):
        helptext = ""
        for category in Category:
            helptext += f'\n > ### {category.value} \n > '
            for command in self.client.commands:
                if command.usage == category:
                    helptext += f'`{command}` '
        await ctx.send(f'> ### Hier sind alle nutzbaren commands \n > {helptext}')


    @commands.command(name="shutdown", help="Stoppt den Bot", usage=Category.settings)
    async def shutdown(self, ctx):
        await ctx.send("Shutting down")
        await self.client.close()


async def setup(client):
    await client.add_cog(Settings(client))
