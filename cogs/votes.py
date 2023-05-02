import discord
from discord.ext import commands, tasks
import json
import datetime
import sys
import os
sys.path.append(os.path.abspath("../utils"))
from utils.discord_helpers.gui_assets import *
from utils.discord_helpers.access import *
from utils.vote.vote_object import *

class Votes(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.fetchet_votes = {}
		self.votecache = {}

	@tasks.loop(minutes=5)
	async def voteloop(self):
		...

	@is_staff()
	@commands.slash_command()
	async def create_vote(self, ctx, data: discord.Option(str, "JSON строка")):
		vote = Vote(self.bot)
		try:
			vote.parse_json(data)					
		except:
			await ctx.respond("Ошибка ввода данных!")
			return
		vote.author = ctx.author.id
		await vote.send_message()
		vote.upload_to_database()
		await ctx.respond("Готово!")

def setup(bot):
	bot.add_cog(Votes(bot))
	print("[Lesbian Wathcer] votes engaged!")