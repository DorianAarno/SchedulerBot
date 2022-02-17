from disnake import *
from disnake.ext import commands
import sqlite3
import traceback

db = sqlite3.connect('assets/data.sqlite')
cursor = db.cursor()

async def DataFetch(bot, command, table, *vals):
    try:
        # There is no use for bot parameter in Sqlite3 but on migration to cloud database like postgresql, you will need it.
        query = f"SELECT * FROM {table}"
        if len(vals) == 1:
            query += f' WHERE guild_id = {vals[0]}'
        elif len(vals) == 2:
            query += f' WHERE guild_id = {vals[0]} and user_id = {vals[1]}'
        else:
            pass
        cursor.execute(query)
        if command == 'all':
            return cursor.fetchall()
        else:
            return cursor.fetchone()
    except:
        print(traceback.format_exc())

async def DataUpdate(bot, query, *vals):
    if len(vals) == 0:
        cursor.execute(query)
    else:
        cursor.execute(query, vals)
    db.commit()

def SuccessEmbed(title, description):
    return Embed(title=":ballot_box_with_check: "+title, description=description, color=Color.green())

def ErrorEmbed(title, description):
    return Embed(title=":x: "+title, description=description, color=Color.from_rgb(255,0,0))

class ConfirmationButtons(ui.View):
    def __init__(self, authorid):
        super().__init__(timeout=120.0)
        self.value = None
        self.authorid = authorid
    @ui.button(emoji="✖️", style=ButtonStyle.red)
    async def first_button(self, button, inter):
        if inter.author.id != self.authorid:
            return await inter.send("You cannot interact with these buttons.", ephemeral=True)
        self.value = False
        for button in self.children:
            button.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()
    @ui.button(emoji="✔️", style=ButtonStyle.green)
    async def second_button(self, button, inter):
        if inter.author.id != self.authorid:
            return await inter.send("You cannot interact with these buttons.", ephemeral=True)
        self.value = True
        for button in self.children:
            button.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()
