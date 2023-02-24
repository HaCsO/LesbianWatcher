import discord
from discord.ext import commands, tasks
import sqlite3
import json
import datetime
from ..utils.discord_helpers.gui_assets import *

class Votes(commands.Cog):
	def __init__(self, bot):

		self.bot = bot

def setup(bot):
	bot.add_cog(Votes(bot))
	print("[Lesbian Wathcer] votes engaged!")