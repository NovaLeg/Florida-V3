import discord
from discord.ext import commands
import sqlite3

class WelcomeSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("wlc.db")
        self.cursor = self.db.cursor()
        self.create_tables()
        self.default_welcome = "Welcome {{mention}} to {{server}}! We now have {{members}} members."
        self.default_leave = "Goodbye {{username}}! Hope to see you again in {{server}}."

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS welcome_settings (
                guild_id INTEGER PRIMARY KEY,
                welcome_channel_id INTEGER,
                leave_channel_id INTEGER,
                welcome_message TEXT,
                leave_message TEXT
            )
        """)
        self.db.commit()

    def format_message(self, message, member):
        return message.replace("{{username}}", member.name)\
                      .replace("{{mention}}", member.mention)\
                      .replace("{{discrim}}", member.discriminator)\
                      .replace("{{id}}", str(member.id))\
                      .replace("{{server}}", member.guild.name)\
                      .replace("{{members}}", str(member.guild.member_count))

    async def send_embed(self, ctx, description, color=0x2b2d31):
        embed = discord.Embed(description=description, color=color)
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    async def set_channel(self, ctx, channel, channel_type):
        if not ctx.channel.permissions_for(ctx.guild.me).send_messages:
            await self.send_embed(ctx, "I don't have permission to send messages in this channel.")
            return

        guild_id = ctx.guild.id
        self.cursor.execute("SELECT * FROM welcome_settings WHERE guild_id = ?", (guild_id,))
        if self.cursor.fetchone() is None:
            self.cursor.execute(
                "INSERT INTO welcome_settings (guild_id, welcome_channel_id, leave_channel_id, welcome_message, leave_message) VALUES (?, ?, ?, ?, ?)",
                (guild_id, None, None, self.default_welcome, self.default_leave)
            )

        if channel_type == "welcome":
            self.cursor.execute("UPDATE welcome_settings SET welcome_channel_id = ? WHERE guild_id = ?", (channel.id, guild_id))
            description = f"Welcome channel has been set to {channel.mention}."
        elif channel_type == "leave":
            self.cursor.execute("UPDATE welcome_settings SET leave_channel_id = ? WHERE guild_id = ?", (channel.id, guild_id))
            description = f"Leave channel has been set to {channel.mention}."

        self.db.commit()
        await self.send_embed(ctx, description)

    @commands.hybrid_command(aliases=['setwlc'], usage="Set the welcome channel", help="Sets the welcome channel where new members will be greeted.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def setwelcome(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            await self.send_embed(ctx, "Please specify a valid channel!")
            return
        await self.set_channel(ctx, channel, "welcome")

    @commands.hybrid_command(aliases=['setlv'], usage="Set the leave channel", help="Sets the leave channel where members will be waved goodbye.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def setleave(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            await self.send_embed(ctx, "Please specify a valid channel!")
            return
        await self.set_channel(ctx, channel, "leave")

    @commands.hybrid_command(aliases=['resetwlc'], usage="Reset the welcome channel", help="Resets the welcome channel, no more welcome messages will be sent.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def resetwelcome(self, ctx):
        guild_id = ctx.guild.id
        self.cursor.execute("UPDATE welcome_settings SET welcome_channel_id = NULL WHERE guild_id = ?", (guild_id,))
        self.db.commit()
        await self.send_embed(ctx, "Welcome channel has been reset. No more welcome messages will be sent.")

    @commands.hybrid_command(aliases=['resetlv'], usage="Reset the leave channel", help="Resets the leave channel, no more leave messages will be sent.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def resetleave(self, ctx):
        guild_id = ctx.guild.id
        self.cursor.execute("UPDATE welcome_settings SET leave_channel_id = NULL WHERE guild_id = ?", (guild_id,))
        self.db.commit()
        await self.send_embed(ctx, "Leave channel has been reset. No more leave messages will be sent.")

    @commands.hybrid_command(aliases=['setwelcmsg'], usage="Set the welcome message", help="Sets a custom welcome message for new members.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def setwelcomemessage(self, ctx, *, message: str):
        guild_id = ctx.guild.id
        self.cursor.execute("UPDATE welcome_settings SET welcome_message = ? WHERE guild_id = ?", (message, guild_id))
        self.db.commit()
        await self.send_embed(ctx, "Welcome message updated.")

    @commands.hybrid_command(aliases=['setlvmsg'], usage="Set the leave message", help="Sets a custom leave message for departing members.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def setleavemessage(self, ctx, *, message: str):
        guild_id = ctx.guild.id
        self.cursor.execute("UPDATE welcome_settings SET leave_message = ? WHERE guild_id = ?", (message, guild_id))
        self.db.commit()
        await self.send_embed(ctx, "Leave message updated.")

    @commands.hybrid_command(aliases=['settingsview'], usage="View server settings", help="Displays the current welcome/leave settings for this server.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def viewsettings(self, ctx):
        guild_id = ctx.guild.id
        self.cursor.execute("SELECT welcome_channel_id, leave_channel_id, welcome_message, leave_message FROM welcome_settings WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result:
            welcome_channel_id, leave_channel_id, welcome_message, leave_message = result
            welcome_channel = self.bot.get_channel(welcome_channel_id) if welcome_channel_id else None
            leave_channel = self.bot.get_channel(leave_channel_id) if leave_channel_id else None

            description = (
                f"**Welcome Channel:** {welcome_channel.mention if welcome_channel else 'Not Set'}\n"
                f"**Leave Channel:** {leave_channel.mention if leave_channel else 'Not Set'}\n"
                f"**Welcome Message:** {welcome_message if welcome_message else self.default_welcome}\n"
                f"**Leave Message:** {leave_message if leave_message else self.default_leave}\n"
                f"\n**Customizable Variables:**\n"
                f"{{{{username}}}} - User's name\n"
                f"{{{{mention}}}} - User's mention\n"
                f"{{{{discrim}}}} - User's discriminator\n"
                f"{{{{id}}}} - User's ID\n"
                f"{{{{server}}}} - Server name\n"
                f"{{{{members}}}} - Server member count"
            )

            await self.send_embed(ctx, description)
        else:
            await self.send_embed(ctx, "No configuration found for this server.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        self.cursor.execute("SELECT welcome_channel_id, welcome_message FROM welcome_settings WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result:
            welcome_channel_id, welcome_message = result
            welcome_channel = self.bot.get_channel(welcome_channel_id) if welcome_channel_id else None
            if welcome_channel:
                if not welcome_message:
                    welcome_message = self.default_welcome
                message = self.format_message(welcome_message, member)
                await welcome_channel.send(message)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = member.guild.id
        self.cursor.execute("SELECT leave_channel_id, leave_message FROM welcome_settings WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result:
            leave_channel_id, leave_message = result
            leave_channel = self.bot.get_channel(leave_channel_id) if leave_channel_id else None
            if leave_channel:
                if not leave_message:
                    leave_message = self.default_leave
                message = self.format_message(leave_message, member)
                await leave_channel.send(message)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
