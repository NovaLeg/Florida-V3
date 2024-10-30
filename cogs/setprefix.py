import discord
from discord.ext import commands
import sqlite3

class SetPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = sqlite3.connect('prefix.db')
        self.cursor = self.config.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS config (guild INTEGER PRIMARY KEY, prefix TEXT)")
        self.config.commit()

    @commands.hybrid_command(
        name="setprefix", 
        aliases=["changeprefix"], 
        usage="/setprefix <new_prefix>", 
        help="Change the bot's prefix for this server."
    )
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(send_messages=True)
    async def set_prefix(self, ctx: commands.Context, new_prefix: str):
        embed = discord.Embed()
        embed.color = 0x2b2d31

        if not new_prefix:
            embed.description = "Prefix cannot be empty."
            embed.set_author(name="Prefix Change Failed", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed, ephemeral=True)
            return

        if len(new_prefix) > 10:
            embed.description = "Prefix cannot be longer than 10 characters."
            embed.set_author(name="Prefix Change Failed", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed, ephemeral=True)
            return

        if ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed.description = "You must have a role above me to change the prefix."
            embed.set_author(name="Prefix Change Failed", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed, ephemeral=True)
            return

        self.cursor.execute("INSERT OR REPLACE INTO config (guild, prefix) VALUES (?, ?)", (ctx.guild.id, new_prefix))
        self.config.commit()

        embed.description = f"Prefix updated to `{new_prefix}`"
        embed.set_author(name=f"Prefix Changed by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"New Prefix: {new_prefix}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SetPrefix(bot))
