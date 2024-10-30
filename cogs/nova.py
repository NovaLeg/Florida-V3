import discord
from discord.ext import commands
import re
import datetime

time_regex = re.compile(r'(\d+)([smhd])')

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = {}

    async def send_embed_dm(self, member, title, description):
        embed = discord.Embed(title=title, description=description, color=0x2b2d31)
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.hybrid_command(name="role", with_app_command=True, description="Add/Remove a role from a user")
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def role(self, ctx, member: discord.Member, role: discord.Role):
        bot_owner_id = self.bot.owner_id

        if ctx.author.id == bot_owner_id:
            pass
        elif not ctx.author.guild_permissions.manage_roles:
            await ctx.message.add_reaction('<:info:1297452289489113168>')
            return

        if ctx.guild.me.top_role.position > role.position:
            if role in member.roles:
                await member.remove_roles(role)
                await self.send_embed_dm(member, "Role Removed", f"You have had the role **{role.name}** removed in **{ctx.guild.name}**.")
            else:
                await member.add_roles(role)
                await self.send_embed_dm(member, "Role Added", f"You have been given the role **{role.name}** in **{ctx.guild.name}**.")
            await ctx.message.add_reaction('<:check:1297452315007127612>')
        else:
            await ctx.message.add_reaction('<:info:1297452289489113168> ')

    @commands.hybrid_command(name="ban", with_app_command=True, description="Ban a member")
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ban(self, ctx, member: discord.User, *, reason=None):
        bot_owner_id = self.bot.owner_id

        if ctx.author.id == bot_owner_id:
            pass
        elif not ctx.author.guild_permissions.ban_members:
            await ctx.message.add_reaction('<:info:1297452289489113168>')
            return

        try:
            await self.send_embed_dm(member, "You Have Been Banned", f"You have been banned from **{ctx.guild.name}** for: {reason}")
        except discord.Forbidden:
            pass

        try:
            await ctx.guild.ban(member, reason=reason)
            await ctx.message.add_reaction('<:check:1297452315007127612>')
        except discord.Forbidden:
            await ctx.message.add_reaction('<:info:1297452289489113168>')

    @commands.hybrid_command(name="unban", with_app_command=True, description="Unban a member")
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def unban(self, ctx, *, member):
        bot_owner_id = self.bot.owner_id

        if ctx.author.id == bot_owner_id:
            pass
        elif not ctx.author.guild_permissions.ban_members:
            await ctx.message.add_reaction('<:info:1297452289489113168>')
            return

        banned_users = await ctx.guild.bans()

        if member.isdigit():
            member_id = int(member)
            for ban_entry in banned_users:
                if ban_entry.user.id == member_id:
                    await ctx.guild.unban(ban_entry.user)
                    await ctx.message.add_reaction('<:check:1297452315007127612>')
                    return
        elif len(member.split('#')) == 2:
            member_name, member_discriminator = member.split('#')
            for ban_entry in banned_users:
                if (ban_entry.user.name, ban_entry.user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(ban_entry.user)
                    await ctx.message.add_reaction('<:check:1297452315007127612>')
                    return

        await ctx.message.add_reaction('<:info:1297452289489113168>')

    @commands.hybrid_command(name="mute", with_app_command=True, description="Timeout a user for a specific time")
    @commands.has_permissions(moderate_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def timeout(self, ctx, member: discord.Member, duration: str, reason: str = None):
        bot_owner_id = self.bot.owner_id

        if ctx.author.id == bot_owner_id:
            pass
        elif not ctx.author.guild_permissions.moderate_members:
            await ctx.message.add_reaction('<:info:1297452289489113168>')
            return

        total_seconds = 0
        matches = time_regex.findall(duration)

        for amount, unit in matches:
            amount = int(amount)
            if unit == 's':
                total_seconds += amount
            elif unit == 'm':
                total_seconds += amount * 60
            elif unit == 'h':
                total_seconds += amount * 3600
            elif unit == 'd':
                total_seconds += amount * 86400

        if total_seconds <= 0:
            await ctx.message.add_reaction('<:check:1297452315007127612>')
            return

        timeout_duration = datetime.timedelta(seconds=total_seconds)

        try:
            await member.timeout(timeout_duration, reason=reason)
            await ctx.message.add_reaction('<:check:1297452315007127612>')
        except discord.Forbidden:
            await ctx.message.add_reaction('<:info:1297452289489113168>')

    @commands.hybrid_command(name="unmute", with_app_command=True, description="Unmute a member")
    @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def untimeout(self, ctx, member: discord.Member):
        bot_owner_id = self.bot.owner_id

        if ctx.author.id == bot_owner_id:
            pass
        elif not ctx.author.guild_permissions.moderate_members:
            await ctx.message.add_reaction('<:info:1297452289489113168>')
            return

        if member.timed_out_until:
            try:
                await member.edit(timed_out_until=None)
                await ctx.message.add_reaction('<:check:1297452315007127612>')
            except Exception:
                await ctx.message.add_reaction('<:info:1297452289489113168>')
        else:
            await ctx.message.add_reaction('<:info:1297452289489113168>')

    @commands.hybrid_command(name="warn", with_app_command=True, description="Warn a member")
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        bot_owner_id = self.bot.owner_id

        if ctx.author.id == bot_owner_id:
            pass
        elif not ctx.author.guild_permissions.manage_messages:
            await ctx.message.add_reaction('<:info:1297452289489113168>')
            return

        if member.id not in self.warns:
            self.warns[member.id] = []

        self.warns[member.id].append(reason)

        await self.send_embed_dm(member, "You Have Been Warned", f"You have been warned in **{ctx.guild.name}** for: {reason}")
        await ctx.message.add_reaction('<:check:1297452315007127612>')

    @commands.hybrid_command(name="attach", aliases=["media"], with_app_command=True, description="Grant attach file permissions to a user in a channel")
    @commands.has_permissions(manage_guild=True)
    async def picperms(self, ctx, user: discord.User = None, channel: discord.TextChannel = None):
        if not isinstance(ctx.channel, discord.TextChannel):
            embed = discord.Embed(
                description="This command can only be used in a text channel.",
               color=0x2b2d31
            )
            return await ctx.send(embed=embed)

        if user is None:
            embed = discord.Embed(
                description="The correct way to use the command is:\n`attach <user> [#channel]`\n\n-# **For Example**\n-# attach @nova #chat\n\n-# **Aliases:** media",
                color=0x2b2d31
            )
            return await ctx.send(embed=embed)

        target_channel = channel if channel else ctx.channel
        overwrite = discord.PermissionOverwrite(attach_files=True, embed_links=True)

        try:
            await target_channel.set_permissions(user, overwrite=overwrite)
            embed = discord.Embed(
                description=f"{ctx.author.mention}: **Attach File permissions** have been granted to {user.mention} in {target_channel.mention}.",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"An error occurred while granting permissions: {e}",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)
            
    @commands.hybrid_command(name="kick", with_app_command=True, description="Kick a member")
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kick(self, ctx, member: discord.User, *, reason=None):
        bot_owner_id = self.bot.owner_id

        if ctx.author.id == bot_owner_id:
            pass
        elif not ctx.author.guild_permissions.kick_members:
            await ctx.message.add_reaction('<:info:1297452289489113168>')
            return

        try:
            await self.send_embed_dm(member, "You Have Been Kicked", f"You have been kicked from **{ctx.guild.name}** for: {reason}")
        except discord.Forbidden:
            pass

        try:
            await ctx.guild.kick(member, reason=reason)
            await ctx.message.add_reaction('<:check:1297452315007127612>')
        except discord.Forbidden:
            await ctx.message.add_reaction('<:info:1297452289489113168>')

    async def send_embed_dm(self, member, title, description):
        embed = discord.Embed(title=title, description=description, color=0x2b2d31) 
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

    async def send_embed_dm(self, member, title, description):
        embed = discord.Embed(title=title, description=description, color=0x2b2d31)
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.hybrid_command(name="lock", with_app_command=True, description="Lock a channel")
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        overwrite = target_channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await target_channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.message.add_reaction('<:check:1297452315007127612>')

    @commands.hybrid_command(name="unlock", with_app_command=True, description="Unlock a channel")
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        overwrite = target_channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await target_channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.message.add_reaction('<:check:1297452315007127612>')

    @commands.hybrid_command(name="hide", with_app_command=True, description="Hide a channel")
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hide(self, ctx, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        overwrite = target_channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = False
        await target_channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.message.add_reaction('<:check:1297452315007127612>')

    @commands.hybrid_command(name="unhide", with_app_command=True, description="Unhide a channel")
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def unhide(self, ctx, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        overwrite = target_channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = True
        await target_channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.message.add_reaction('<:check:1297452315007127612>')

async def setup(bot):
    await bot.add_cog(Moderation(bot))
    
