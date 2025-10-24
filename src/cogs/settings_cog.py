from __future__ import annotations

import re

from discord.ext import commands

from src.service import settings_service
from src.service.util_service import Category


class Settings(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(
        name="Contact", help="Sendet Nachricht an eine Person", usage=Category.settings
    )
    async def contact(self, ctx, *, arg):
        regex = r"\d{18}"
        match = re.search(regex, arg)
        if match:
            user_id = match.group()
            user = await self.client.fetch_user(int(user_id))
            if user:
                await user.send(re.sub(regex, "", arg))
                await ctx.send(f"Nachricht gesendet an: {user_id}")
            else:
                await ctx.send("Fehler beim senden, sorry ;(")
        else:
            await ctx.send("Es muss eine 18-stellige UserID angegeben werden!")

    @commands.command(
        name="help", help="Bessere version von help", usage=Category.settings
    )
    async def help(self, ctx):
        helptext = ""
        for category in Category:
            helptext += f"\n > ### {category.value} \n > "
            for command in self.client.commands:
                if command.usage == category:
                    helptext += f"`{command}` "
        await ctx.send(f"> ### Hier sind alle nutzbaren commands \n > {helptext}")

    @commands.command(name="shutdown", help="Stoppt den Bot", usage=Category.settings)
    async def shutdown(self, ctx):
        await ctx.send("Shutting down")
        await self.client.close()

    @commands.command(
        name="set_birthday_channel",
        help="Set channel for birthday announcements (mention or id).",
        usage=Category.settings,
    )
    async def set_birthday_channel(self, ctx, channel: str = None):
        """Set the birthday channel. If no channel provided, uses current channel."""
        cid = None
        if channel is None:
            cid = ctx.channel.id
        else:
            # Accept mention like <#123...> or raw id
            m = re.search(r"(\d{17,20})", channel)
            if m:
                cid = int(m.group(1))
        if cid is None:
            await ctx.send(
                "Could not determine channel id. Provide a channel mention or id."
            )
            return

        # Save as guild-scoped setting
        guild_id = ctx.guild.id if ctx.guild else 0
        settings_service.set_setting("birthday_channel_id", str(cid), guild_id=guild_id)
        await ctx.send(f"Birthday channel set to <#{cid}>")

    @commands.command(
        name="get_birthday_channel",
        help="Show the configured birthday channel for this guild.",
        usage=Category.settings,
    )
    async def get_birthday_channel(self, ctx):
        guild_id = ctx.guild.id if ctx.guild else 0
        val = settings_service.get_setting("birthday_channel_id", guild_id=guild_id)
        if val:
            await ctx.send(f"Configured birthday channel: <#{val}>")
        else:
            await ctx.send("No birthday channel configured for this guild.")


async def setup(client):
    await client.add_cog(Settings(client))
