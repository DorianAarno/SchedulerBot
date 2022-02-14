from disnake import *
from disnake.ext import commands
import os, traceback

bot = commands.Bot(case_insensitive=True, command_prefix='.', intents=Intents.default())

@bot.event
async def on_ready():
    print('*********\nBot is Ready.\n*********')

# bot.remove_command('help')

@bot.command()
async def ping(ctx):
    await ctx.send (f"📶 {round(bot.latency * 1000)}ms")

# @bot.event
# async def on_command_error(ctx,error):
#     if isinstance(error, (commands.CommandNotFound)):
#         return

for file in os.listdir('./cogs'):
    if file.endswith('.py') and file != '__init__.py':
        try:
            bot.load_extension("cogs."+file[:-3])
            print(f"{file[:-3]} Loaded successfully.")
        except:
            print(f"Unable to load {file[:-3]}.")
            print(traceback.format_exc())

bot.run('ODYwNDAxMDg2Mjc1MTI1MjQ4.YN6s9A.em6BE1C34Gu23qpAY18Fo2VBHMQ')
