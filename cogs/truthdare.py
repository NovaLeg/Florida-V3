import discord
import random
import aiohttp
from discord.ext import commands

class TruthDare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_truth(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.truthordarebot.xyz/api/truth') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['question']
    
    async def fetch_dare(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.truthordarebot.xyz/api/dare') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['question']

    async def create_embed(self, ctx, title, description):
        embed = discord.Embed(description=description, color=0x2b2d31)
        embed.set_author(name=f"{ctx.author.display_name} chose {title}", icon_url=ctx.author.avatar.url)
        return embed

    @commands.hybrid_command(name="truth", with_app_command=True, description="Get a truth question.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def truth(self, ctx):
        truth_question = await self.fetch_truth()
        embed = await self.create_embed(ctx, "Truth", truth_question)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="dare", with_app_command=True, description="Get a dare question.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dare(self, ctx):
        dare_question = await self.fetch_dare()
        embed = await self.create_embed(ctx, "Dare", dare_question)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="random", with_app_command=True, description="Get a random truth or dare.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def random_command(self, ctx):
        choice = random.choice(["truth", "dare"])
        if choice == "truth":
            truth_question = await self.fetch_truth()
            embed = await self.create_embed(ctx, "Truth", truth_question)
        else:
            dare_question = await self.fetch_dare()
            embed = await self.create_embed(ctx, "Dare", dare_question)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TruthDare(bot))
