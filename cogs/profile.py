from discord.ext import commands
from discord import Embed, ui

class Xd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_badges(self, member):
        badges = []
        if member.id == 1142754238179594240 or member.id == 1084285203616366712:
            badges.append("<:check:1297452315007127612> **Developer**\n")
        
        role_mapping = {
            1294285800900661439: "**Owner**",
            1294285830193680384: "**Admin**",
            1294285884929347706: "**Moderator**",
            1294285935663644754: "**Support Team**",
            1294285977388580893: "**Special**"
        }

        for role_id, role_name in role_mapping.items():
            if any(role.id == role_id for role in member.roles):
                badges.append(f"<:check:1297452315007127612> {role_name}\n")

        badges.append("<:check:1297452315007127612> **Normal User**")
        return badges

    @commands.hybrid_command(aliases=['pr', 'pf'], usage="shows the user's profile and badges", help="Show badges of a user")
    async def profile(self, ctx, member: commands.MemberConverter = None):
        member = member or ctx.author
        badges = self.get_badges(member)

        embed = Embed(color=0x2b2d31)
        embed.set_author(name=f"{member.name}", icon_url=member.avatar.url)
        embed.description = f"{''.join(badges)}"

        view = ui.View()
        button = ui.Button(label="Support", url="https://discord.gg/h3MbgTYD")
        view.add_item(button)

        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Profile(bot))
