from disnake import *
from disnake.ext import commands
import os, traceback
from assets import functions as func

bot = commands.Bot(case_insensitive=True, command_prefix='*', intents=Intents.default())

@bot.event
async def on_ready():
    print('*********\nBot is Ready.\n*********')

async def CheckAdmin(ctx):
    if ctx.author.guild_permissions.administrator:
        return True
    else:
        await ctx.send(embed=func.ErrorEmbed('Missing Permissions', 'You are missing permissions. You need to have `administrator` permission in order to use this bot.'))
        return False

bot.remove_command('help')
bot.check_once(CheckAdmin)

@bot.command()
async def ping(ctx):
    await ctx.send (f"📶 {round(bot.latency * 1000)}ms")

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
        return

for file in os.listdir('./cogs'):
    if file.endswith('.py') and file != '__init__.py':
        try:
            bot.load_extension("cogs."+file[:-3])
            print(f"{file[:-3]} Loaded successfully.")
        except:
            print(f"Unable to load {file[:-3]}.")
            print(traceback.format_exc())

bot.run('ODYwNDAxMDg2Mjc1MTI1MjQ4.YN6s9A.em6BE1C34Gu23qpAY18Fo2VBHMQ')
