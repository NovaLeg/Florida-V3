import os
import discord
from discord.ext import tasks
from zipfile import ZipFile
import io

class BackupManager:
    def __init__(self, bot):
        self.bot = bot
        self.excluded_folders = ['.local', '.pythonlibs', '.upm', '.cache']
        self.owner_ids = [1142754238179594240, 1084285203616366712]

    @tasks.loop(hours=1)
    async def start_backup(self):
        backup_buffer = io.BytesIO()
        with ZipFile(backup_buffer, 'w') as backup_zip:
            for folder_name, subfolders, filenames in os.walk('.'):
                if any(excluded in folder_name for excluded in self.excluded_folders):
                    continue
                for filename in filenames:
                    file_path = os.path.join(folder_name, filename)
                    backup_zip.write(file_path)
        backup_buffer.seek(0)

        for owner_id in self.owner_ids:
            user = await self.bot.fetch_user(owner_id)
            if user:
                try:
                    user_backup_buffer = io.BytesIO(backup_buffer.getvalue())
                    dm_channel = await user.create_dm()
                    async for message in dm_channel.history(limit=15):
                        if message.author == self.bot.user:
                            try:
                                await message.delete()
                            except discord.HTTPException:
                                pass 
                    await user.send(file=discord.File(user_backup_buffer, filename='florida-backup.zip'))

                except Exception as e:
                    print(f"Failed to send backup to {user}: {e}")

        backup_buffer.close()

    @start_backup.before_loop
    async def before_backup(self):
        await self.bot.wait_until_ready()

    def start(self):
        self.start_backup.start()
