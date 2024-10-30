from discord import Embed, Interaction
from discord.ext import commands
import discord
import time

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.hybrid_command(aliases=['latency'], usage="Shows the bot's latency", help="Bot latency")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx):
        embed = Embed(color=0x2b2d31)
        embed.description = f"My latency: **{round(self.bot.latency * 1000)}ms**"
        embed.set_author(name="Florida", icon_url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(aliases=['information', 'info'], usage="Shows app metadata", help="Bot Metadata")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def metadata(self, ctx):
        embed = Embed(color=0x2b2d31)
        embed.description = f"<:check:1297452315007127612> **Metadata**\n\n<:info:1297452289489113168> **Project Name :** florida\n<:info:1297452289489113168> **Description :** a bit more than a multipurpose bot i guess ?\n<:info:1297452289489113168> **Author :** nova\n<:info:1297452289489113168> **Repository URL :** https://github.com/NovaLeg/Florida"
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(usage="Shows this help menu", help="Help menu")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def help(self, ctx: commands.Context):
        embed = Embed(color=0x2b2d31)
        embed.description = """<:info:1297452289489113168> `My global prefix is & (Changeable).`
<:info:1297452289489113168> `Made and maintained by Florida developers.`
<:info:1297452289489113168> `Select an option below to view commands.`"""
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

        options = [
            discord.SelectOption(emoji="<:info:1297452289489113168>", label="Go to homepage", value="home"),
            discord.SelectOption(emoji="<:info:1297452289489113168>", label="Welcome & leave commands", value="welcome"),
              discord.SelectOption(emoji="<:info:1297452289489113168>", label="Moderation commands", value="moderation"),
            discord.SelectOption(emoji="<:info:1297452289489113168>", label="Giveaway commands", value="giveaway"),
            discord.SelectOption(emoji="<:info:1297452289489113168>", label="Truth or dare commands", value="truth_or_dare"),
            
 discord.SelectOption(emoji="<:info:1297452289489113168>", label="Economy commands", value="economy"),
            discord.SelectOption(emoji="<:info:1297452289489113168>", label="Minigame commands", value="minigame"),
            discord.SelectOption(emoji="<:info:1297452289489113168>", label="Information commands", value="info"),
        ]

        select = discord.ui.Select(placeholder="Select a category to view commands", options=options)

        async def callback(interaction: Interaction):
            if select.values[0] == "home":
                embed = Embed(color=0x2b2d31)
                embed.description = """<:info:1297452289489113168> `My global prefix is & (Changeable).`
<:info:1297452289489113168> `Made and maintained by Florida developers.`
<:info:1297452289489113168> `Select an option below to view commands.`"""
            elif select.values[0] == "welcome":
                embed = Embed(title="<:check:1297452315007127612> Welcome & Leave Commands", color=0x2b2d31)
                embed.description = """
<:info:1297452289489113168> **`setwelcome` -** `Set welcome messages`
<:info:1297452289489113168> **`setleave` -** `Set leave messages`
<:info:1297452289489113168> **`setwelcomemessage` -** `Customize welcome message`
<:info:1297452289489113168> **`setleavemessage` -** `Customize leave message`
<:info:1297452289489113168> **`settingsview` -** `View the current settings`
                """
            elif select.values[0] == "messages":
                embed = Embed(title="<:check:1297452315007127612> Message Commands", color=0x2b2d31)
                embed.description = """
<:info:1297452289489113168> **`messages` -** `View message count`
<:info:1297452289489113168> **`message add` -** `Add messages manually`
<:info:1297452289489113168> **`leaderboard` -** `View the top message leaders`
                """
            elif select.values[0] == "moderation":
                embed = Embed(title="<:check:1297452315007127612> Moderation Commands", color=0x2b2d31)
                embed.description = """
<:info:1297452289489113168> **`mute` -** `Mute a user`
<:info:1297452289489113168> **`unmute` -** `Unmute a user`
<:info:1297452289489113168> **`ban` -** `Ban a user`
<:info:1297452289489113168> **`kick` -** `Kick a user`
<:info:1297452289489113168> **`unban` -** `Unban a user`
<:info:1297452289489113168> **`warn` -** `Warn a user`
<:info:1297452289489113168> **`lock` -** `Lock a channel`
<:info:1297452289489113168> **`unlock` -** `Unlock a channel`
<:info:1297452289489113168> **`hide` -** `Hide a channel`
<:info:1297452289489113168> **`unhide` -** `Unhide a channel`
                """
            elif select.values[0] == "giveaway":
                embed = Embed(title="<:check:1297452315007127612> Giveaway Commands", color=0x2b2d31)
                embed.description = """
<:info:1297452289489113168> **`gstart` -** `Start a giveaway`
<:info:1297452289489113168> **`gend` -** `End a giveaway`
<:info:1297452289489113168> **`greroll` -** `Reroll a giveaway winner`
                """
            elif select.values[0] == "truth_or_dare":
                embed = Embed(title="<:check:1297452315007127612> Truth or Dare Commands", color=0x2b2d31)
                embed.description = """
<:info:1297452289489113168> **`truth` -** `Ask a truth`
<:info:1297452289489113168> **`dare` -** `Dare someone`
<:info:1297452289489113168> **`random` -** `Play random Truth or Dare`
                """
            elif select.values[0] == "images":
                embed = Embed(title="<:check:1297452315007127612> Anime Image Commands", color=0x2b2d31)
                embed.description = """
<:info:1297452289489113168> **`kiss` -** `Send a kiss image`
<:info:1297452289489113168> **`hug` -** `Send a hug image`
                """
            elif select.values[0] == "economy":
                embed = Embed(title="<:check:1297452315007127612> Economy Commands", color=0x2b2d31)
                embed.description = """
<:info:1297452289489113168>**`balance` -** `Check your balance`
<:info:1297452289489113168> **`buy` -** `buy a ring`
<:info:1297452289489113168> **`divorce` -** `Divorce with your partner`
<:info:1297452289489113168> **`economy_leaderboard` -** `Shows the economy leaderboard`
<:info:1297452289489113168> **`marry` -** `Propose a user`
<:info:1297452289489113168> **`marriage` -** `Show marriage details`
<:info:1297452289489113168> **`shop` -** `View the shop`
<:info:1297452289489113168> **`pay` -** `Transfer money to a another user`
<:info:1297452289489113168> **`work` -** `Work and earn money`
<:info:1297452289489113168> **`withdraw` -** `Withdraw money from your bank`
                """
            elif select.values[0] == "minigame":
                embed = Embed(title="<:check:1297452315007127612> Minigame Commands", color=0x2b2d31)
                embed.description = """
<:info:1297452289489113168> **`coinflip` -** `Flip a coin`
<:info:1297452289489113168> **`minesweeper` -** `Play minesweeper`
<:info:1297452289489113168> **`doubledice` -** `Role two dice`
                """
            elif select.values[0] == "info":
                embed = Embed(title="<:check:1297452315007127612> Information Commands", color=0x2b2d31)
                embed.description = """
<:info:1297452289489113168> **`help` -** `Shows bot help command`
<:info:1297452289489113168> **`userinfo` -** `Shows user information`
<:info:1297452289489113168> **`ping` -** `Shows bot latency`
<:info:1297452289489113168> **`profile` -** `Shows user profile`
<:info:1297452289489113168> **`serverinfo` -** `Shows server information`
                """

            await interaction.response.edit_message(embed=embed)

        select.callback = callback

        view = discord.ui.View()
        view.add_item(select)

        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Info(bot))
