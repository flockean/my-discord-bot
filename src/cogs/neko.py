from discord.ext import commands
from src.controller.util_service import Category
from src.service.api import neko_best

class Neko(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(usage=Category.interaction)
    async def neko(self, ctx):
        await ctx.send(neko_best("neko"))


    @commands.command(usage=Category.interaction)
    async def waifu(self, ctx):
        await ctx.send(neko_best("waifu"))


    @commands.command(usage=Category.interaction)
    async def husbando(self, ctx):
        await ctx.send(neko_best("husbando"))


    @commands.command(usage=Category.interaction)
    async def kitsune(self, ctx):
        await ctx.send(neko_best("kitsune"))


    @commands.command(usage=Category.interaction)
    async def lurk(self, ctx):
        await ctx.send(neko_best("lurk"))


    @commands.command(usage=Category.interaction)
    async def shoot(self, ctx):
        await ctx.send(neko_best("shoot"))


    @commands.command(usage=Category.interaction)
    async def sleep(self, ctx):
        await ctx.send(neko_best("sleep"))


    @commands.command(usage=Category.interaction)
    async def shrug(self, ctx):
        await ctx.send(neko_best("shrug"))


    @commands.command(usage=Category.interaction)
    async def stare(self, ctx):
        await ctx.send(neko_best("stare"))


    @commands.command(usage=Category.interaction)
    async def wave(self, ctx):
        await ctx.send(neko_best("wave"))


    @commands.command(usage=Category.interaction)
    async def poke(self, ctx):
        await ctx.send(neko_best("poke"))


    @commands.command(usage=Category.interaction)
    async def smile(self, ctx):
        await ctx.send(neko_best("smile"))


    @commands.command(usage=Category.interaction)
    async def peck(self, ctx):
        await ctx.send(neko_best("peck"))


    @commands.command(usage=Category.interaction)
    async def wink(self, ctx):
        await ctx.send(neko_best("wink"))


    @commands.command(usage=Category.interaction)
    async def blush(self, ctx):
        await ctx.send(neko_best("blush"))


    @commands.command(usage=Category.interaction)
    async def smug(self, ctx):
        await ctx.send(neko_best("smug"))


    @commands.command(usage=Category.interaction)
    async def tickle(self, ctx):
        await ctx.send(neko_best("tickle"))


    @commands.command(usage=Category.interaction)
    async def yeet(self, ctx):
        await ctx.send(neko_best("yeet"))


    @commands.command(usage=Category.interaction)
    async def think(self, ctx):
        await ctx.send(neko_best("think"))


    @commands.command(usage=Category.interaction)
    async def highfive(self, ctx):
        await ctx.send(neko_best("highfive"))


    @commands.command(usage=Category.interaction)
    async def feed(self, ctx):
        await ctx.send(neko_best("feed"))


    @commands.command(usage=Category.interaction)
    async def bite(self, ctx):
        await ctx.send(neko_best("bite"))


    @commands.command(usage=Category.interaction)
    async def bored(self, ctx):
        await ctx.send(neko_best("bored"))


    @commands.command(usage=Category.interaction)
    async def nom(self, ctx):
        await ctx.send(neko_best("nom"))


    @commands.command(usage=Category.interaction)
    async def yawn(self, ctx):
        await ctx.send(neko_best("yawn"))


    @commands.command(usage=Category.interaction)
    async def facepalm(self, ctx):
        await ctx.send(neko_best("facepalm"))


    @commands.command(usage=Category.interaction)
    async def cuddle(self, ctx):
        await ctx.send(neko_best("cuddle"))


    @commands.command(usage=Category.interaction)
    async def kick(self, ctx):
        await ctx.send(neko_best("kick"))


    @commands.command(usage=Category.interaction)
    async def happy(self, ctx):
        await ctx.send(neko_best("happy"))


    @commands.command(usage=Category.interaction)
    async def hug(self, ctx):
        await ctx.send(neko_best("hug"))


    @commands.command(usage=Category.interaction)
    async def baka(self, ctx):
        await ctx.send(neko_best("baka"))


    @commands.command(usage=Category.interaction)
    async def pat(self, ctx):
        await ctx.send(neko_best("pat"))


    @commands.command(usage=Category.interaction)
    async def nod(self, ctx):
        await ctx.send(neko_best("nod"))


    @commands.command(usage=Category.interaction)
    async def nope(self, ctx):
        await ctx.send(neko_best("nope"))


    @commands.command(usage=Category.interaction)
    async def kiss(self, ctx):
        await ctx.send(neko_best("kiss"))


    @commands.command(usage=Category.interaction)
    async def dance(self, ctx):
        await ctx.send(neko_best("dance"))


    @commands.command(usage=Category.interaction)
    async def punch(self, ctx):
        await ctx.send(neko_best("punch"))


    @commands.command(usage=Category.interaction)
    async def handshake(self, ctx):
        await ctx.send(neko_best("handshake"))


    @commands.command(usage=Category.interaction)
    async def slap(self, ctx):
        await ctx.send(neko_best("slap"))


    @commands.command(usage=Category.interaction)
    async def cry(self, ctx):
        await ctx.send(neko_best("cry"))


    @commands.command(usage=Category.interaction)
    async def pout(self, ctx):
        await ctx.send(neko_best("pout"))


    @commands.command(usage=Category.interaction)
    async def handhold(self, ctx):
        await ctx.send(neko_best("handhold"))


    @commands.command(usage=Category.interaction)
    async def thumbsup(self, ctx):
        await ctx.send(neko_best("thumbsup"))


    @commands.command(usage=Category.interaction)
    async def laugh(self, ctx):
        await ctx.send(neko_best("laugh"))

async def setup(client):
    await client.add_cog(Neko(client))
