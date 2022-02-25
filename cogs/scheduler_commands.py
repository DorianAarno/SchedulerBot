from disnake import *
from disnake.ext.commands import *
from assets import functions as func
import traceback
from datetime import datetime, timedelta
import asyncio
from cogs.help import Help

class DropDownSchedule(ui.Select):
    def __init__(self, bot, ctx, datas, command, vals):
        self.bot = bot
        self.ctx = ctx
        self.datas = datas
        self.command = command
        self.vals = vals
        options = []
        for data in datas:
            time = datetime.strptime(data[1], '%Y-%m-%d %H:%M:%S.%f')
            time_now = datetime.utcnow()
            diff = time - time_now
            second_diff = diff.seconds
            day_diff = diff.days
            if time < time_now:
                time = 'Time has passed.'
            else:
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
        if inter.author.id != self.ctx.author.id:
            return await inter.send("You cannot interact with this menu.", ephemeral=True)

        async def EditCommandCheck(data):
            channel = self.vals[0]
            content = self.vals[1]

            if channel == "None":
                channel = self.bot.get_channel(data[10])
            if content == "None":
                content = data[2]
            if '0' in self.command:
                embed = 0
            else:
                embed = 1
            await func.DataUpdate(self.bot, f"DELETE FROM schedules WHERE guild_id = {inter.guild.id} and num = {self.values[0]}")
            for data in reversed(self.datas):
                if data[9] == int(self.values[0]):
                    self.datas.remove(data)
            for i, data in enumerate(self.datas):
                await func.DataUpdate(self.bot, f"UPDATE schedules SET num = {i+1} WHERE guild_id = {inter.guild.id} and num = {data[9]}")
            await SchedulerCommands.ScheduleAdd(self, self.ctx, channel, data[1], content, embed, 'edit')

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
                            if 'https' in data[7] or 'http' in data[7]:
                                embed.set_image(url=data[7])
                        except:
                            pass
                    if data[8] != "None":
                        embed.color = data[8]
                    if self.command == 'remove':
                        view = func.ConfirmationButtons(inter.author.id)
                        await inter.send(content="Are you sure this is the schedule you want to delete?", embed=embed, view=view)
                        await view.wait()
                        if view.value:
                            await func.DataUpdate(self.bot, f"DELETE FROM schedules WHERE guild_id = {inter.guild.id} and num = {self.values[0]}")
                            for data in reversed(self.datas):
                                if data[9] == int(self.values[0]):
                                    self.datas.remove(data)
                            for i, data in enumerate(self.datas):
                                await func.DataUpdate(self.bot, f"UPDATE schedules SET num = {i+1} WHERE guild_id = {inter.guild.id} and num = {data[9]}")
                            await self.ctx.send(embed=func.SuccessEmbed('Schedule Removed!', 'Schedule was deleted successfully.'))
                    elif 'edit' in self.command:
                        view = func.ConfirmationButtons(inter.author.id)
                        await inter.send(content="Are you sure this is the schedule you want to edit?", embed=embed, view=view)
                        await view.wait()
                        if view.value:
                            await EditCommandCheck(data)
                    else:
                        await inter.send(embed=embed)

                else:
                    message = data[2]
                    if data[7] != "None":
                        try:
                            message += f'\n\n{data[7]}'
                        except:
                            pass
                    if self.command == 'remove':
                        view = func.ConfirmationButtons(inter.author.id)
                        await inter.send(content="Are you sure this is the schedule you want to delete?\n\n"+message, allowed_mentions=AllowedMentions.none(), view=view)
                        await view.wait()
                        if view.value:
                            await func.DataUpdate(self.bot, f"DELETE FROM schedules WHERE guild_id = {inter.guild.id} and num = {self.values[0]}")
                            for data in reversed(self.datas):
                                if data[9] == int(self.values[0]):
                                    self.datas.remove(data)
                            for i, data in enumerate(self.datas):
                                await func.DataUpdate(self.bot, f"UPDATE schedules SET num = {i+1} WHERE guild_id = {inter.guild.id} and num = {data[9]}")
                            await self.ctx.send(embed=func.SuccessEmbed('Schedule Removed!', 'Schedule was deleted successfully.'))
                    elif 'edit' in self.command:
                        view = func.ConfirmationButtons(inter.author.id)
                        await inter.send(content="Are you sure this is the schedule you want to edit?\n\n"+message, allowed_mentions=AllowedMentions.none(), view=view)
                        await view.wait()
                        if view.value:
                            await EditCommandCheck(data)
                    else:
                        await inter.send(content=message)

class DropdownView(ui.View):
    def __init__(self, bot, ctx, datas, command, *vals):
        super().__init__()
        length = len(datas)
        if length > 25:
            for i in range(0, length, 25):
                self.add_item(DropDownSchedule(bot, ctx, datas[:25], command, vals))
                del datas[:25]
        else:
            self.add_item(DropDownSchedule(bot, ctx, datas, command, vals))

class SchedulerCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @group(invoke_without_command=True, case_insensitive=True)
    async def schedule(self, ctx):
        await Help.schedule(self, ctx)

    @schedule.group(invoke_without_command=True, case_insensitive=True)
    async def add(self, ctx):
        await Help.schedule(self, ctx)

    async def CheckDuration(self, duration):
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
    async def message(self, ctx, channel: TextChannel, duration, *, message):
        await self.ScheduleAdd(ctx, channel, duration, message, 0)

    @message.error
    async def message_Error(self, ctx, error):
        if isinstance(error, (BadArgument, MissingRequiredArgument)):
            await ctx.send(embed=func.ErrorEmbed('Syntax Error', 'Correct syntax is: `*schedule add message <#channel> <duration> <message>`. Example: `*schedule add message #general 10h Hello Everyone!`'))

    async def ScheduleAdd(self, ctx, channel, duration, description, embed, command="add"):
        if command == 'add':
            time = await SchedulerCommands.CheckDuration(self, duration)
            if time == "Exception 1":
                return await ctx.send(embed=func.ErrorEmbed('Error', 'Time needs to be followed by either of the following. `w/d/h/m`'))
            elif time == "Exception 2":
                return await ctx.send(embed=func.ErrorEmbed('Error', 'Invalid format. Duration needs to be be like `2h`, `2w`, etc.'))
            else:
                pass
        else:
            time = duration
        await ctx.send(embed=Embed(title="Loop", description="Input how many times you want the schedule to loop. Type `0` for infinite loop. `1` will be taken in case of wrong input."))
        loop = await self.bot.wait_for('message', check=lambda m: m.channel.id == ctx.channel.id and m.author.id == ctx.author.id, timeout=300.0)
        try:
            loop_integer = int(loop.content)
        except:
            loop_integer = 1
        if embed == 0:
            await ctx.send(embed=Embed(description="Now input the attachment you need with the message. Type `None` to skip it.", title="Attachment"))
            msg = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=360.0)
            if len(msg.attachments) == 0:
                attachment = msg.content
            else:
                attachment = msg.attachments[0].url
            datas = await func.DataFetch(self.bot, 'all', 'schedules', ctx.guild.id)
            await func.DataUpdate(self.bot, f"INSERT INTO schedules(guild_id, time, embed, response, title, footer, thumbnail, color, attachment, num, channel_id, loop_integer, timedelta) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", ctx.guild.id, time, 0, description, "None", "None", "None", "None", attachment, len(datas)+1, channel.id, loop_integer, str(duration))
            await ctx.send(embed=func.SuccessEmbed('Schedule Added!', "Schedule added successfully."))
        else:
            elements = [None]*5
            current_element = 0
            element_name = "Title"
            while None in elements:
                await ctx.send(embed=Embed(title=element_name, description=f"Now input a {element_name} for the embed, Type `None` to skip it."))
                msg = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=360.0)
                if msg.content.lower() == 'none':
                    msg.content = "None"
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
            datas = await func.DataFetch(self.bot, 'all', 'schedules', ctx.guild.id)
            await func.DataUpdate(self.bot, f"INSERT INTO schedules(guild_id, time, embed, response, title, footer, thumbnail, color, attachment, num, channel_id, loop_integer, timedelta) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", ctx.guild.id, time, 1, description, elements[0], elements[1], elements[2], elements[3], elements[4], len(datas)+1, channel.id, loop_integer, str(duration))
            await ctx.send(embed=func.SuccessEmbed('Schedule Added!', "Schedule added successfully."))

    @add.command()
    async def embed(self, ctx, channel: TextChannel, duration, *, description):
        try:
            await self.ScheduleAdd(ctx, channel, duration, description, 1)
        except:
            print(traceback.format_exc())

    @embed.error
    async def embed_Error(self, ctx, error):
        if isinstance(error, (BadArgument, MissingRequiredArgument)):
            await ctx.send(embed=func.ErrorEmbed('Syntax Error', 'Correct syntax is: `*schedule add embed <#channel> <duration> <message>`. Example: `.schedule add embed #general 10h Hello Everyone!`'))

    @schedule.command()
    async def overview(self, ctx):
        try:
            datas = await func.DataFetch(self.bot, 'all', 'schedules', ctx.guild.id)
            if len(datas) == 0:
                return await ctx.send(embed=func.ErrorEmbed('Error', 'There are no active schedules.'))
            await ctx.send(embed=Embed(title="Select a Schedule", description="Here's a list of all schedules with their trigger time. Select any one of them to see their embed/message."), view=DropdownView(self.bot, ctx, datas, 'overview'))
        except:
            print(traceback.format_exc())

    @schedule.command()
    async def remove(self, ctx):
        datas = await func.DataFetch(self.bot, 'all', 'schedules', ctx.guild.id)
        if len(datas) == 0:
            return await ctx.send(embed=func.ErrorEmbed('Error', 'There are no active schedules.'))
        await ctx.send(embed=Embed(title="Select a Schedule", description="Here's a list of all schedules with their trigger time. Select any one of them to see their embed/message and delete them."), view=DropdownView(self.bot, ctx, datas, 'remove'))

    @schedule.group(invoke_without_command=True, case_insensitive=True)
    async def edit(self, ctx):
        await Help.schedule(self, ctx)

    @edit.command(name='message')
    async def message_edit(self, ctx, channel:TextChannel = "None", * , message):
        datas = await func.DataFetch(self.bot, 'all', 'schedules', ctx.guild.id)
        await ctx.send(embed=Embed(title="Select a schedule", description="Here's a list of all schedules with their trigger time. Select any one of them to see their embed/message and edit them."), view=DropdownView(self.bot, ctx, datas, 'edit:0', channel, message))

    @message_edit.error
    async def message_edit_Error(self, ctx, error):
        if isinstance(error, (BadArgument, MissingRequiredArgument)):
            await ctx.send(embed=func.ErrorEmbed('Syntax Error', 'Correct syntax is: `*schedule edit message <#channel> <content>`.'))

    @edit.command(name='embed')
    async def embed_edit(self, ctx, channel:TextChannel = "None", * , description):
        datas = await func.DataFetch(self.bot, 'all', 'schedules', ctx.guild.id)
        if len(datas) == 0:
            return await ctx.send(embed=func.ErrorEmbed('Error', 'There are no active schedules.'))
        await ctx.send(embed=Embed(title="Select a Schedule", description="Here's a list of all schedules with their trigger time. Select any one of them to see their embed/message and edit them."), view=DropdownView(self.bot, ctx, datas, 'edit:1', channel, description))

    @embed_edit.error
    async def embed_edit_Error(self, ctx, error):
        if isinstance(error, (BadArgument, MissingRequiredArgument)):
            await ctx.send(embed=func.ErrorEmbed('Syntax Error', 'Correct syntax is: `*schedule edit embed <#channel> <description>`.'))

def setup(bot):
    bot.add_cog(SchedulerCommands(bot))
