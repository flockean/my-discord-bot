import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src import cogs
from src.cogs.settings import Settings
from src.controller import util_service
from src.controller.util_service import Category
from src.database import database_utils
from src.models.schemas import DMMessage
import src.cogs.game_mgmt
import src.cogs.neko
import src.cogs.settings
from src.cogs.game_mgmt import GameMmgt

# Generate Discord-Bot client
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents, command_prefix="f!_")
logging.basicConfig(level=logging.INFO)
client.remove_command('help')


def start_bot():
    load_dotenv()
    # Start the bot
    client.run(os.getenv('DISCORD_BOT'))


@client.event
async def on_ready():
    logging.info("BotStats: " + str(client.user) + " Id: " + str(client.application_id))
    await src.cogs.settings.setup(client)
    await src.cogs.neko.setup(client)
    await src.cogs.game_mgmt.setup(client)
    logging.info("Bot is now Ready")


@client.command(name="RandomJoke", help="Gibt dir ein zufälligen schlechten Witz", usage=Category.rest)
async def joke(ctx):
    await ctx.send(util_service.random_joke())


@client.command(name="nsfw", help="Gibt ein random Nsfw Bild", usage=Category.nsfw)
async def nsfw(ctx):
    await ctx.send("Leider gerade nicht aktiv! <:Screenshot20240514161554:1291407970646757386>")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Es scheint ein Argument zu fehlen, probiere nochmal mit: ***f!_[befehl] [message]***")


@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if msg.guild is None:
        database_utils.add(DMMessage(author=msg.author.name, content=msg.content))
    logging.info(f'{msg.author}: {msg.content}')
    await client.process_commands(msg)
