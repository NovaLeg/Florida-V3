import discord
from discord.ext import commands
from discord.ui import Button, View

class Ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.idle)
        activity = discord.Activity(type=discord.ActivityType.watching, name="&help")
        await self.bot.change_presence(activity=activity)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return

        if self.bot.user.mentioned_in(message):
            mentions = [mention for mention in message.mentions if mention == self.bot.user]
            if mentions and message.content.strip() == mentions[0].mention:
                embed = discord.Embed(
                    description=f"Hey {message.author.mention}, my global prefix is `&`.\n\nWhat would you like to do today?\nUse `&help` or `/help` to start your journey.",
                    color=0x2b2d31
                )

                support_button = Button(label="Add To Server", url="https://discord.com/oauth2/authorize?client_id=933233761263419452")
                invite_button = Button(label="Support Server", url="https://discord.gg/PGgDqYxb6N")

                view = View()
                view.add_item(support_button)
                view.add_item(invite_button)

                await message.channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Ready(bot))

