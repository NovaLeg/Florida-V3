import discord
from discord.ext import commands
import sqlite3
import asyncio
import random
from datetime import datetime, timedelta

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('wow.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                               (user_id INTEGER PRIMARY KEY, balance INTEGER, bank INTEGER, partner_id INTEGER, ring_type TEXT, married_date TEXT, daily_used TEXT, last_work TEXT)''')
        self.db.commit()

    def get_user(self, user_id):
        self.cursor.execute("SELECT balance, bank, partner_id, ring_type, married_date, daily_used, last_work FROM users WHERE user_id = ?", (user_id,))
        user = self.cursor.fetchone()
        if user is None:
            self.cursor.execute("INSERT INTO users (user_id, balance, bank) VALUES (?, ?, ?)", (user_id, 1000, 0))
            self.db.commit()
            return 1000, 0, None, None, None, None, None
        return user

    def update_user(self, user_id, balance=None, bank=None, partner_id=None, ring_type=None, married_date=None, daily_used=None, last_work=None):
        query = "UPDATE users SET "
        params = []
        if balance is not None:
            query += "balance = ?, "
            params.append(balance)
        if bank is not None:
            query += "bank = ?, "
            params.append(bank)
        if partner_id is not None:
            query += "partner_id = ?, "
            params.append(partner_id)
        if ring_type is not None:
            query += "ring_type = ?, "
            params.append(ring_type)
        if married_date is not None:
            query += "married_date = ?, "
            params.append(married_date)
        if daily_used is not None:
            query += "daily_used = ?, "
            params.append(daily_used)
        if last_work is not None:
            query += "last_work = ?, "
            params.append(last_work)
        
        query = query.rstrip(', ') + " WHERE user_id = ?"
        params.append(user_id)
        self.cursor.execute(query, tuple(params))
        self.db.commit()

    def create_embed(self, description):
        embed = discord.Embed(description=description, color=0x2b2d31)
        return embed

    @commands.hybrid_command(usage="Buy a ring to propose", help="/shop")
    async def shop(self, ctx):
        rings = [
            {"name": "Common Ring", "price": 1000, "emoji": "💍"},
            {"name": "Uncommon Ring", "price": 5000, "emoji": "🥉"},
            {"name": "Legendry Ring", "price": 10000, "emoji": "🥈"},
            {"name": "Rare Ring", "price": 20000, "emoji": "🥇"},
            {"name": "Diamond Ring", "price": 50000, "emoji": "💎"},
            {"name": "Nova Ring", "price": 100000, "emoji": "👑"}
        ]
        
        description = "Welcome to the shop! Here are the rings you can buy:\n"
        for ring in rings:
            description += f"{ring['emoji']} **{ring['name']}** - ${ring['price']:,}\n"

        await ctx.send(embed=self.create_embed(description))

    @commands.hybrid_command(usage="Buy a ring", help="/buy <ring_name>")
    async def buy(self, ctx, ring_name: str):
        rings = {
            "common": {"name": "Common Ring", "price": 1000, "emoji": "💍"},
            "uncommon": {"name": "Uncommon Ring", "price": 5000, "emoji": "🥉"},
            "legendary": {"name": "Legendry Ring", "price": 10000, "emoji": "🥈"},
            "epic": {"name": "Epic Ring", "price": 20000, "emoji": "🥇"},
            "diamond": {"name": "Diamond Ring", "price": 50000, "emoji": "💎"},
            "nova": {"name": "Nova Ring", "price": 100000, "emoji": "👑"}
        }
        user_id = ctx.author.id
        balance, _, _, ring_type, _, _, _ = self.get_user(user_id)
        
        ring = rings.get(ring_name.lower())
        if ring is None:
            await ctx.send(embed=self.create_embed(f"{ring_name} is not a valid ring! Check the shop for valid options."))
            return
        
        if balance < ring['price']:
            await ctx.send(embed=self.create_embed(f"You don't have enough money to buy the {ring['name']}!"))
            return
        
        balance -= ring['price']
        self.update_user(user_id, balance=balance, ring_type=ring['name'])
        await ctx.send(embed=self.create_embed(f"You bought the {ring['emoji']} **{ring['name']}**!"))

    @commands.hybrid_command(usage="Propose to another user", help="/marry @user")
    async def marry(self, ctx, partner: discord.Member):
        proposer_id = ctx.author.id
        partner_id = partner.id
        
        balance, _, _, ring_type, _, _, _ = self.get_user(proposer_id)
        _, _, current_partner, _, _, _, _ = self.get_user(partner_id)

        if ring_type is None:
            await ctx.send(embed=self.create_embed("You need to buy a ring first before proposing!"))
            return

        if current_partner:
            await ctx.send(embed=self.create_embed(f"{partner.name} is already married!"))
            return

        if partner == ctx.author:
            await ctx.send(embed=self.create_embed("You can't marry yourself!"))
            return

        await ctx.send(f"{partner.mention}, {ctx.author.name} is proposing to you with a {ring_type}. Type `accept` or `deny` within 30 seconds.")

        def check(m):
            return m.author == partner and m.content.lower() in ['accept', 'deny']

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(embed=self.create_embed("The proposal has timed out!"))
            return

        if msg.content.lower() == 'deny':
            await ctx.send(embed=self.create_embed(f"{partner.name} denied the proposal."))
        elif msg.content.lower() == 'accept':
            married_date = datetime.now().strftime("%Y-%m-%d")
            self.update_user(proposer_id, partner_id=partner_id, married_date=married_date)
            self.update_user(partner_id, partner_id=proposer_id, married_date=married_date)
            await ctx.send(embed=self.create_embed(f"{ctx.author.name} and {partner.name} are now married! 💍"))

    @commands.hybrid_command(usage="Divorce your partner", help="/divorce")
    async def divorce(self, ctx):
        user_id = ctx.author.id
        balance, _, partner_id, _, _, _, _ = self.get_user(user_id)

        if partner_id is None:
            await ctx.send(embed=self.create_embed("You are not married!"))
            return

        self.update_user(user_id, partner_id=None, ring_type=None, married_date=None)
        self.update_user(partner_id, partner_id=None, ring_type=None, married_date=None)
        await ctx.send(embed=self.create_embed(f"You have divorced your partner. 💔"))

    @commands.hybrid_command(usage="Show marriage details", help="/marriage")
    async def marriage(self, ctx):
        user_id = ctx.author.id
        balance, _, partner_id, ring_type, married_date, _, _ = self.get_user(user_id)

        if partner_id is None:
            await ctx.send(embed=self.create_embed("You are not married!"))
            return

        partner = self.bot.get_user(partner_id)
        days_since_married = (datetime.now() - datetime.strptime(married_date, "%Y-%m-%d")).days
        await ctx.send(embed=self.create_embed(f"You are married to {partner.name} with the {ring_type}. Married on {married_date} ({days_since_married} days ago). 💍"))

    @commands.hybrid_command(usage="Work and earn money", help="/work")
    async def work(self, ctx):
        user_id = ctx.author.id
        balance, _, partner_id, _, _, _, last_work = self.get_user(user_id)

        if last_work and datetime.strptime(last_work, "%Y-%m-%d %H:%M:%S") + timedelta(hours=24) > datetime.now():
            await ctx.send(embed=self.create_embed("You have already worked today. Come back later."))
            return
        
        work_amount = random.randint(100, 500)
        balance += work_amount
        self.update_user(user_id, balance=balance, last_work=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if partner_id:
            partner_balance, _, _, _, _, _, _ = self.get_user(partner_id)
            partner_bonus = work_amount * 0.1
            partner_balance += partner_bonus
            self.update_user(partner_id, balance=partner_balance)
            await ctx.send(embed=self.create_embed(f"You worked and earned ${work_amount:,}. Your partner also received a bonus of ${int(partner_bonus):,}."))

        await ctx.send(embed=self.create_embed(f"You worked and earned ${work_amount:,}. Your new balance is ${balance:,}."))

    @commands.hybrid_command(usage="Check your balance", help="/balance")
    async def balance(self, ctx):
        user_id = ctx.author.id
        balance, bank, _, _, _, _, _ = self.get_user(user_id)
        await ctx.send(embed=self.create_embed(f"Your balance is ${balance:,}.\nBank balance: ${bank:,}."))

    @commands.hybrid_command(usage="Deposit money into your bank", help="/deposit <amount>")
    async def deposit(self, ctx, amount: int):
        user_id = ctx.author.id
        balance, bank, _, _, _, _, _ = self.get_user(user_id)

        if amount <= 0:
            await ctx.send(embed=self.create_embed("You must deposit a positive amount."))
            return
        
        if amount > balance:
            await ctx.send(embed=self.create_embed("You do not have enough money to deposit that amount."))
            return
        
        balance -= amount
        bank += amount
        self.update_user(user_id, balance=balance, bank=bank)
        await ctx.send(embed=self.create_embed(f"You have deposited ${amount:,} into your bank. Your new balance is ${balance:,}."))

    @commands.hybrid_command(usage="Withdraw money from your bank", help="/withdraw <amount>")
    async def withdraw(self, ctx, amount: int):
        user_id = ctx.author.id
        balance, bank, _, _, _, _, _ = self.get_user(user_id)

        if amount <= 0:
            await ctx.send(embed=self.create_embed("You must withdraw a positive amount."))
            return
        
        if amount > bank:
            await ctx.send(embed=self.create_embed("You do not have enough money in your bank to withdraw that amount."))
            return
        
        balance += amount
        bank -= amount
        self.update_user(user_id, balance=balance, bank=bank)
        await ctx.send(embed=self.create_embed(f"You have withdrawn ${amount:,} from your bank. Your new balance is ${balance:,}."))

    @commands.hybrid_command(usage="Transfer money to another user", help="/pay @user <amount>")
    async def pay(self, ctx, member: discord.Member, amount: int):
        user_id = ctx.author.id
        recipient_id = member.id
        balance, _, _, _, _, _, _ = self.get_user(user_id)

        if amount <= 0:
            await ctx.send(embed=self.create_embed("You must transfer a positive amount."))
            return
        
        if amount > balance:
            await ctx.send(embed=self.create_embed("You do not have enough money to transfer that amount."))
            return

        recipient_balance, _, _, _, _, _, _ = self.get_user(recipient_id)
        balance -= amount
        recipient_balance += amount

        self.update_user(user_id, balance=balance)
        self.update_user(recipient_id, balance=recipient_balance)
        await ctx.send(embed=self.create_embed(f"You have transferred ${amount:,} to {member.mention}. Your new balance is ${balance:,}."))

    @commands.hybrid_command(usage="Show the leaderboard", help="/leaderboard")
    async def economy_leaderboard(self, ctx):
        self.cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
        top_users = self.cursor.fetchall()
        
        description = "Top 10 Users by Balance:\n"
        for rank, (user_id, balance) in enumerate(top_users, start=1):
            user = self.bot.get_user(user_id)
            description += f"{rank}. {user.name if user else 'Unknown User'} - ${balance:,}\n"

        await ctx.send(embed=self.create_embed(description))

    @commands.hybrid_command(usage="Add cash to a user's balance (Bot owner only)", help="/cashadd @user <amount>")
    @commands.is_owner()
    async def cashadd(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send(embed=self.create_embed("You must add a positive amount."))
            return

        user_id = member.id
        balance, _, _, _, _, _, _ = self.get_user(user_id)
        balance += amount
        self.update_user(user_id, balance=balance)
        await ctx.send(embed=self.create_embed(f"Added ${amount:,} to {member.mention}'s balance. New balance: ${balance:,}."))

async def setup(bot):
    await bot.add_cog(Economy(bot))
