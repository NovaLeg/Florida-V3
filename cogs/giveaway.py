import discord
from discord.ext import commands, tasks
import sqlite3
import random
from datetime import datetime, timedelta

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('giveaway.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS giveaways 
                          (message_id INTEGER PRIMARY KEY, channel_id INTEGER, prize TEXT, 
                           end_time INTEGER, winners INTEGER)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS participants 
                          (user_id INTEGER, message_id INTEGER)''')
        self.conn.commit()

    @tasks.loop(seconds=30)
    async def check_giveaway(self):
        current_time = int(datetime.now().timestamp())
        self.c.execute("SELECT * FROM giveaways WHERE end_time <= ?", (current_time,))
        ended_giveaways = self.c.fetchall()
        for giveaway in ended_giveaways:
            await self.end_giveaway(giveaway[0])
            self.c.execute("DELETE FROM giveaways WHERE message_id = ?", (giveaway[0],))
        self.conn.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_giveaway.is_running():
            self.check_giveaway.start()

    @commands.command()
    async def gstart(self, ctx, duration: str, winners: int, *, prize: str):
        end_time = self.parse_duration(duration)
        if end_time is None:
            await ctx.send("Invalid duration! Example: 1d, 1h, 1m")
            return

        embed = discord.Embed(
            title=f"🎉 Giveaway 🎉",
            description=f"**Prize:** {prize}\n**Duration:** {duration}\n**Winners:** {winners}",
            color=0x2b2d31,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Ends in {duration}")

        giveaway_message = await ctx.send(embed=embed)
        await giveaway_message.add_reaction("🎉")

        self.c.execute("INSERT INTO giveaways (message_id, channel_id, prize, end_time, winners) VALUES (?, ?, ?, ?, ?)",
                       (giveaway_message.id, ctx.channel.id, prize, end_time, winners))
        self.conn.commit()

    @commands.command()
    async def gend(self, ctx, message_id: int):
        self.c.execute("SELECT * FROM giveaways WHERE message_id = ?", (message_id,))
        giveaway = self.c.fetchone()
        if not giveaway:
            await ctx.send("Giveaway not found!")
            return
        await self.end_giveaway(message_id)

    @commands.command()
    async def greroll(self, ctx, message_id: int):
        self.c.execute("SELECT * FROM giveaways WHERE message_id = ?", (message_id,))
        giveaway = self.c.fetchone()
        if not giveaway:
            await ctx.send("Giveaway not found!")
            return
        await self.reroll_winner(message_id)

    async def end_giveaway(self, message_id):
        self.c.execute("SELECT * FROM participants WHERE message_id = ?", (message_id,))
        participants = self.c.fetchall()
        if not participants:
            return

        self.c.execute("SELECT * FROM giveaways WHERE message_id = ?", (message_id,))
        giveaway = self.c.fetchone()

        channel = self.bot.get_channel(giveaway[1])
        prize = giveaway[2]
        winners = giveaway[4]

        winner_ids = self.choose_winners(participants, winners)
        winners_mention = ", ".join(f"<@{winner}>" for winner in winner_ids)

        await channel.send(f"🎉 Congratulations {winners_mention}! You won **{prize}**!")
        self.c.execute("DELETE FROM participants WHERE message_id = ?", (message_id,))
        self.conn.commit()

    async def reroll_winner(self, message_id):
        self.c.execute("SELECT * FROM participants WHERE message_id = ?", (message_id,))
        participants = self.c.fetchall()
        if not participants:
            return

        self.c.execute("SELECT * FROM giveaways WHERE message_id = ?", (message_id,))
        giveaway = self.c.fetchone()

        channel = self.bot.get_channel(giveaway[1])
        prize = giveaway[2]
        winners = giveaway[4]

        winner_ids = self.choose_winners(participants, winners)
        winners_mention = ", ".join(f"<@{winner}>" for winner in winner_ids)

        await channel.send(f"🎉 The giveaway has been rerolled! New winner(s): {winners_mention} for **{prize}**!")

    def choose_winners(self, participants, num_winners):
        winner_ids = []
        participants_set = set(participant[0] for participant in participants)
        for _ in range(num_winners):
            if not participants_set:
                break
            winner = random.choice(list(participants_set))
            winner_ids.append(winner)
            participants_set.remove(winner)
        return winner_ids

    def parse_duration(self, duration):
        amount = int(duration[:-1])
        unit = duration[-1]
        if unit == 'd':
            return int((datetime.now() + timedelta(days=amount)).timestamp())
        elif unit == 'h':
            return int((datetime.now() + timedelta(hours=amount)).timestamp())
        elif unit == 'm':
            return int((datetime.now() + timedelta(minutes=amount)).timestamp())
        return None

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name != "🎉":
            return
        self.c.execute("SELECT * FROM giveaways WHERE message_id = ?", (payload.message_id,))
        if not self.c.fetchone():
            return
        self.c.execute("INSERT INTO participants (user_id, message_id) VALUES (?, ?)", (payload.user_id, payload.message_id))
        self.conn.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.emoji.name != "🎉":
            return
        self.c.execute("DELETE FROM participants WHERE user_id = ? AND message_id = ?", (payload.user_id, payload.message_id))
        self.conn.commit()

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
