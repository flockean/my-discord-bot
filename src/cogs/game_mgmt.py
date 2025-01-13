from discord.ext import commands

from src.controller.util_service import Category, fancy_enumeration, fancy_enumeration_categorys
from src.database import database_utils
from src.database.database_utils import *
from src.service.game_mgmt_service import get_all_games, get_all_types, create_game, create_type
from src.models.schemas import Gameprogress, Gamegenre, ProgressStatus
import re
import logging


class GameMmgt(commands.Cog):
    input_single = r'(\w+)'
    input_full = r'"(\w+:\w+")'
    input_full_game = r'(\w+:)'

    def __init__(self, client):
        self.client = client



    # TODO: does not work at please fix
    @commands.command(usage=Category.management, name="getGames")
    async def get_games(self, ctx):
        logging.info("getgames has been triggerd")
        games = get_all_games(get_db())
        if games == None:
            await ctx.send("Sorry Nothing there")
        logging.info(games)
        await ctx.send(games)

    @commands.command(usage=Category.management, name="getCats")
    async def get_category(self, ctx):
        categorys = get_all_types(get_db())
        if categorys == None:
            await ctx.send("Sorry Nothing there")
        logging.info(categorys)
        await ctx.send(categorys)

    @commands.command(usage=Category.management, name="setCat")
    async def set_category(self, ctx, *, args):
        logging.info(args)
        matches = re.findall(self.input_single, args)
        if matches:
            logging.info(matches)
            for match in matches:
                create_type(Gamegenre(name=match), get_db())
        await ctx.send("Category created")

    # TODO: does not work yet
    @commands.command(usage=Category.management, name="setGame")
    async def set_game(self, ctx, *, args):
        matches = re.findall(self.input_single, args)
        if matches:
            logging.info(matches)
            for match in matches:
                create_game(Gameprogress(name=match,
                                         type_id="Hamburger",
                                         in_progress=ProgressStatus.notStarted
                                         ), get_db())

        await ctx.send("Game has been added")


async def setup(client):
    await client.add_cog(GameMmgt(client))
