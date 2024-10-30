import sqlite3
import discord
from discord.ext import commands
from discord import Embed

class Loda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('autoresponder.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS autoresponder 
                               (server_id INTEGER, trigger TEXT, response TEXT)''')
        self.conn.commit()

    def has_manage_guild_permission():
        async def predicate(ctx):
            return ctx.author.guild_permissions.manage_guild
        return commands.check(predicate)

    @commands.hybrid_command(aliases=['ar create'])
    @has_manage_guild_permission()
    async def autoresponder_create(self, ctx, trigger: str, *, response: str):
        server_id = ctx.guild.id
        self.cursor.execute("INSERT INTO autoresponder (server_id, trigger, response) VALUES (?, ?, ?)",
                            (server_id, trigger, response))
        self.conn.commit()
        await ctx.send(f"Successful created: `{trigger}` will respond with `{response}`")

    @commands.hybrid_command(aliases=['ar delete'])
    @has_manage_guild_permission()
    async def autoresponder_delete(self, ctx, trigger: str):
        server_id = ctx.guild.id
        self.cursor.execute("DELETE FROM autoresponder WHERE server_id = ? AND trigger = ?", (server_id, trigger))
        self.conn.commit()
        await ctx.send(f"Successfully deleted autoresponder: `{trigger}`")

    @commands.hybrid_command(aliases=['ar config'])
    @has_manage_guild_permission()
    async def autoresponder_config(self, ctx):
        server_id = ctx.guild.id
        self.cursor.execute("SELECT trigger, response FROM autoresponder WHERE server_id = ?", (server_id,))
        rows = self.cursor.fetchall()
        if rows:
            embed = Embed(title="Autoresponder Config", color=0x2b2d31)
            for trigger, response in rows:
                embed.add_field(name=trigger, value=response, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No autoresponders configured for this server.")

    @commands.hybrid_command(aliases=['ar reset all'])
    @has_manage_guild_permission()
    async def autoresponder_reset_all(self, ctx):
        server_id = ctx.guild.id
        self.cursor.execute("DELETE FROM autoresponder WHERE server_id = ?", (server_id,))
        self.conn.commit()
        await ctx.send("All autoresponders have been reset for this server.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        server_id = message.guild.id
        self.cursor.execute("SELECT trigger, response FROM autoresponder WHERE server_id = ?", (server_id,))
        rows = self.cursor.fetchall()
        for trigger, response in rows:
            if message.content.lower() == trigger.lower():
                await message.channel.send(response)

async def setup(bot):
    await bot.add_cog(Loda(bot))
