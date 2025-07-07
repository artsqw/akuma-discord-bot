import os

import disnake
from disnake.ext import commands

bot = commands.Bot(intents=disnake.Intents.all(), command_prefix="//", status=disnake.Status.idle, help_command=None)


def load_cogs(path="cogs"):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                extension = os.path.join(root, file).replace("\\", ".").replace("/", ".")[:-3]
                try:
                    if extension in bot.extensions:
                        bot.unload_extension(extension)
                    bot.load_extension(extension)
                    print(f"Загружено расширение: {extension}")
                except Exception as e:
                    print(f"Ошибка при загрузке {extension}: {e}")
load_cogs()


bot.run("TOKEN")