from disnake import *
from disnake.ext.commands import *
from assets import functions as func
import traceback
from datetime import datetime
import asyncio

async def ScheduleWatcher(self):
    await self.bot.wait_until_ready()
    while not self.bot.is_closed():
        datas = await func.DataFetch(self.bot, 'all', 'schedules')
        if len(datas) != 0:
            for data in datas:
                try:
                    time = datetime.strptime(data[1], '%Y-%m-%d %H:%M:%S.%f')
                    if time <= datetime.utcnow():
                        channel = self.bot.get_channel(data[10])
                        if data[3] == 0:
                            if data[7] != "None":
                                attachment = f"\n\nAttachments: {data[7]}"
                            else:
                                attachment = ""
                            await channel.send(data[2]+attachment)
                        else:
                            embed = Embed()
                            if data[2] != "None":
                                embed.description = data[2]
                            if data[4] != "None":
                                embed.title = data[4]
                            if data[5] != "None":
                                embed.set_footer(text=data[5])
                            if data[6] != "None":
                                try:
                                    if 'https' in data[6] or 'http' in data[6]:
                                        embed.set_thumbnail(url=data[6])
                                except:
                                    pass
                            if data[7] != "None":
                                try:
                                    embed.set_image(url=data[7])
                                except:
                                    pass
                            if data[8] != "None":
                                embed.color = data[8]
                            await channel.send(embed=embed)
                        await func.DataUpdate(self.bot, f"DELETE FROM schedules WHERE guild_id = {data[0]} and num = {data[9]}")
                        guild_datas = await func.DataFetch(self.bot, 'all', 'schedules', data[0])
                        for i, guild_data in enumerate(guild_datas):
                            await func.DataUpdate(self.bot, f"UPDATE schedules SET num = {i+1} WHERE guild_id = {data[0]} and num = {guild_data[9]}")
                except:
                    print(traceback.format_exc())

        await asyncio.sleep(10)


class SchedulerSystem(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(ScheduleWatcher(self))

def setup(bot):
    bot.add_cog(SchedulerSystem(bot))
