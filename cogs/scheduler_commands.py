from disnake import *
from disnake.ext.commands import *
from assests import functions as func
import traceback
from datetime import datetime, timedelta
import asyncio

class DropDownSchedule(ui.Select):
    def __init__(self, bot, ctx, datas, command):
        self.bot = bot
        self.ctx = ctx
        self.datas = datas
        self.command = command
        options = []
        for data in datas:
            time = datetime.strptime(data[1], '%Y-%m-%d %H:%M:%S.%f')
            diff = time - datetime.utcnow()
            second_diff = diff.seconds
            day_diff = diff.days
            if day_diff < 0:
                time = 'Time has passed.'

            if day_diff == 0:
                if second_diff < 10:
                    time = "Now"
                elif second_diff < 60:
                    time = "In "+str(second_diff) + " seconds"
                elif second_diff < 120:
                    time = "in a minute"
                elif second_diff < 3600:
                    time = "In "+str(second_diff // 60) + " minutes"
                elif second_diff < 7200:
                    time = "in an hour"
                elif second_diff < 86400:
                    time = "In "+str(second_diff // 3600) + " hours"
            elif day_diff == 1:
                time = "Tommorow"
            elif day_diff < 7:
                time = "In "+str(day_diff) + " days"
            elif day_diff < 31:
                time = "In "+str(day_diff // 7) + " weeks"
            elif day_diff < 365:
                time = "In "+str(day_diff // 30) + " months"
            else:
                time = "In "+str(day_diff // 365) + " years"
            options.append(SelectOption(label=time, value=data[9]))
        super().__init__(
            max_values = 1,
            min_values = 1,
            options = options
        )

    async def callback(self, inter):
        await inter.response.defer()
        for data in self.datas:
            if data[9] == int(self.values[0]):
                if data[3] == 1:
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
                    await inter.send(embed=embed)
                else:
                    message = data[2]
                    if data[7] != "None":
                        try:
                            message += f'\n\nAttachment: <{data[7]}>'
                        except:
                            pass
                    await inter.send(message, allowed_mentions=AllowedMentions.none())


class DropdownView(ui.View):
    def __init__(self, bot, ctx, datas, command):
        super().__init__()
        length = len(datas)
        if length > 25:
            for i in range(0, length, 25):
                self.add_item(DropDownSchedule(bot, ctx, datas[:25], command))
                del datas[:25]
        else:
            self.add_item(DropDownSchedule(bot, ctx, datas, command))

class SchedularCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @group(invoke_without_command=True, case_insensitive=True)
    async def schedule(self, ctx):
        pass

    @schedule.group(invoke_without_command=True, case_insensitive=True)
    async def add(self, ctx):
        pass

    async def CheckDuration(self, ctx, duration):
        try:
            time_stamps = ['w', 'd', 'h', 'm']
            duration_check = ''.join([x for x in duration if not x.isdigit()])
            if duration_check.lower() not in time_stamps:
                return "Exception 1"
            for stamp in time_stamps:
                if stamp in duration:
                    try:
                        if stamp == 'w':
                            time = timedelta(weeks=int(duration.replace('w','')))
                        elif stamp == 'd':
                            time = timedelta(days=int(duration.replace('d','')))
                        elif stamp == 'h':
                            time = timedelta(hours=int(duration.replace('h','')))
                        elif stamp == 'm':
                            time = timedelta(minutes=int(duration.replace('m','')))
                        time = str(datetime.utcnow() + time)
                    except:
                        return "Exception 2"
                    break
            return time
        except:
            print(traceback.format_exc())
    @add.command()
    async def message(self, ctx, duration, *, message):
        try:
            time = await self.CheckDuration(ctx, duration)
            if time == "Exception 1":
                return await ctx.send(embed=func.ErrorEmbed('Error', 'Time needs to be followed by either of the following. `w/d/h/m`'))
            elif time == "Exception 2":
                return await ctx.send(embed=func.ErrorEmbed('Error', 'Invalid format. Duration needs to be be like `2h`, `2w`, etc.'))
            else:
                pass
            await ctx.send("Now input the attachment you need with the message. Type `None` to skip it.")
            msg = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=360.0)
            if len(msg.attachments) == 0:
                attachment = msg.content
            else:
                attachment = msg.attachments[0].url
            datas = await func.DataFetch(self.bot, 'all', 'schedules')
            await func.DataUpdate(self.bot, f"INSERT INTO schedules(guild_id, time, embed, response, title, footer, thumbnail, color, attachment, num) VALUES(?,?,?,?,?,?,?,?,?,?)", ctx.guild.id, time, 0, message, "None", "None", "None", "None", attachment, len(datas)+1)
            await ctx.send(embed=func.SuccessEmbed('Schedule Added!', "Schedule added successfully."))
        except:
            print(traceback.format_exc())

    @add.command()
    async def embed(self, ctx, duration, *, description):
        time = await self.CheckDuration(ctx, duration)
        if time == "Exception 1":
            return await ctx.send(embed=func.ErrorEmbed('Error', 'Time needs to be followed by either of the following. `w/d/h/m`'))
        elif time == "Exception 2":
            return await ctx.send(embed=func.ErrorEmbed('Error', 'Invalid format. Duration needs to be be like `2h`, `2w`, etc.'))
        else:
            pass
        elements = [None]*5
        current_element = 0
        element_name = "Title"
        while None in elements:
            await ctx.send(f"Now input a {element_name} for the embed, Type `None` to skip it.")
            msg = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=360.0)
            if current_element == 0:
                elements[current_element] = msg.content
                element_name = "Footer"
            elif current_element == 1:
                element_name = "Thumbnail"
                elements[current_element] = msg.content
            elif current_element == 2:
                element_name = "Color (Hex Code is required, Like `#0000fa`)"
                if len(msg.attachments) == 0:
                    elements[current_element] = msg.content
                else:
                    elements[current_element] = msg.attachments[0].url
            elif current_element == 3:
                element_name = "Attachment/Image"
                try:
                    color = int(msg.content.replace('#',''), 16)
                    elements[current_element] = int(hex(color), 0)
                except:
                    color = "#0000fa"
                    color = int(color.replace('#',''), 16)
                    elements[current_element] = int(hex(color), 0)
            elif current_element == 4:
                if len(msg.attachments) == 0:
                    elements[current_element] = msg.content
                else:
                    elements[current_element] = msg.attachments[0].url
            else:
                break
            current_element += 1
        datas = await func.DataFetch(self.bot, 'all', 'schedules')
        await func.DataUpdate(self.bot, f"INSERT INTO schedules(guild_id, time, embed, response, title, footer, thumbnail, color, attachment, num) VALUES(?,?,?,?,?,?,?,?,?,?)", ctx.guild.id, time, 1, description, elements[0], elements[1], elements[2], elements[3], elements[4], len(datas)+1)
        await ctx.send(embed=func.SuccessEmbed('Schedule Added!', "Schedule added successfully."))

    @schedule.command()
    async def overview(self, ctx):
        datas = await func.DataFetch(self.bot, 'all', 'schedules')
        await ctx.send("Here's a list of all schedules with their trigger time. Select any one of them to see their embed/message.", view=DropdownView(self.bot, ctx, datas, 'overview'))

def setup(bot):
    bot.add_cog(SchedularCommands(bot))
