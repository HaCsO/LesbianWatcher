import discord
from discord.ext import commands
import sqlite3
import json
import datetime
from .gui_assets import *

# additional data structure in db

# warns
# 	moderator
# 	reason
# 	datetime
# unwarns
# 	moderator
# 	reason
# 	datetime

class Mods(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.slash_command()
	async def warns(self, ctx, user: discord.Member):
		view = WarnCard(user, ctx.author, self.bot)
		await ctx.respond(embed= view.update_embed(), view= view)

	@commands.slash_command()
	async def blacklist(self, ctx, user: discord.Member = None):
		...



def setup(bot):
	bot.add_cog(Mods(bot))
	print("Lesbian writer mods engaged!")      