import discord
from discord.ext import commands
import random

class Minigame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='coinflip', with_app_command=True, description="Flip a coin and choose heads or tails.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coin_flip(self, ctx, choice: str):
        if choice.lower() not in ['heads', 'tails']:
            await ctx.send("Choose either 'heads' or 'tails'.")
            return
        
        result = random.choice(['heads', 'tails'])
        outcome = "You win!" if choice.lower() == result else "You lose."
        
        embed = discord.Embed(
            title="Coin Flip",
            description=f"You chose **{choice}**.\nThe coin landed on **{result}**!",
            color=0x2b2d31
        )
        embed.add_field(name="Result", value=outcome, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='minesweeper', with_app_command=True, description="Play Minesweeper with specified size and number of mines.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def minesweeper(self, ctx, size: int = 8, mines: int = 10):
        if size < 2 or mines < 1 or mines >= size ** 2:
            await ctx.send("Invalid size or mines count.")
            return

        board = [['⬜' for _ in range(size)] for _ in range(size)]
        mine_positions = set()

        while len(mine_positions) < mines:
            x, y = random.randint(0, size - 1), random.randint(0, size - 1)
            if (x, y) not in mine_positions:
                mine_positions.add((x, y))
                board[x][y] = '||💣||'

        def adjacent_mines(x, y):
            return sum((nx, ny) in mine_positions
                       for nx in range(x - 1, x + 2)
                       for ny in range(y - 1, y + 2)
                       if 0 <= nx < size and 0 <= ny < size)

        for x in range(size):
            for y in range(size):
                if board[x][y] != '||💣||':
                    count = adjacent_mines(x, y)
                    if count > 0:
                        board[x][y] = f'||{self.num_to_emoji(count)}||'

        board_display = '\n'.join(' '.join(row) for row in board)
        embed = discord.Embed(
            title="Minesweeper",
            description=f"**Board Size:** {size}x{size}\n**Mines:** {mines}\n\n{board_display}",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    def num_to_emoji(self, number):
        emoji_map = {
            1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣',
            6: '6️⃣', 7: '7️⃣', 8: '8️⃣'
        }
        return emoji_map.get(number, '')

    @commands.hybrid_command(name='doubledice', with_app_command=True, description="Roll two dice and compare results.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def double_dice(self, ctx):
        user_roll = random.randint(1, 6) + random.randint(1, 6)
        bot_roll = random.randint(1, 6) + random.randint(1, 6)
        result = "draw" if user_roll == bot_roll else "win" if user_roll > bot_roll else "lose"
        
        embed = discord.Embed(
            title="Double Dice Roll",
            description=f"You rolled: **{user_roll}**\nBot rolled: **{bot_roll}**",
            color=0x2b2d31
        )
        embed.add_field(name="Result", value=f"You {result}!", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Minigame(bot))
