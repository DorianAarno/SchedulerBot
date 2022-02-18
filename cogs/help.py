from disnake import *
from disnake.ext.commands import *

class Help(Cog):
    def __init__(self, bot):
        self.bot = bot

    @group(invoke_without_command=True, case_insensitive=True)
    async def help(self,ctx):
        e = Embed(title=":notepad_spiral: Help Menu :notepad_spiral:", description="• Prefix is *\n•View more about each command using `*help <command-name>`, for Example: `*help schedule`", color=ctx.author.color)
        e.add_field(name="Commands", value="• `schedule`")
        await ctx.send(embed=e)

    @help.command()
    async def schedule(self, ctx):
        e = Embed(title=":calendar: Schedule", description=f"Scheduler system commands.", color=ctx.author.color)
        e.add_field(name="Commands", value="`*schedule add message <#channel> <duration> <message>`: Add a schedule which has to send a message, Duration can be in minute (m), hours (h), weeks (w) and days (d).\n\n`*schedule add embed <#channel> <duration> <description>`: Add a schedule which has to send an embed, Duration can be in minute (m), hours (h), weeks (w) and days (d).\n\n`*schedule remove`: Remove a schedule.\n\n`*schedule overview`: View a list of schedules and their response.\n\n`*schedule edit message <#channel/None> <content>`: Edit active schedules. \n\n`*schedule edit embed <#channel/None> <description>`: Edit active schedules.")
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Help(bot))
