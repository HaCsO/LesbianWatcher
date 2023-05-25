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

	def get_vote_channel(self):
		return self.bot.get_channel_by_known_guild(self.bot.config.channels["vote"])

	async def get_vote_message(self, vote):
		return await self.get_vote_channel().fetch_message(vote.message_id)

	@commands.Cog.listener()
	async def on_ready(self):
		if not self.voteloop.is_running():
			self.voteloop.start()
	
	@tasks.loop(minutes=1)
	async def voteloop(self):
		with self.bot.dbholder.interact() as cur:
			cur.execute("SELECT message_id FROM vote")
			votes = cur.fetchall()

		for i in votes:
			vote = Vote(self.bot)
			vote.grab_from_database(i[0])
			if vote.check_done():
				msg = await self.get_vote_message(vote)
				await vote.edit_message_to_final(msg)
				vote.remove_from_db()
				await self.get_vote_channel().send(vote.get_mentions_str(), delete_after=15)

	@is_staff()
	@commands.slash_command()
	async def check_vote(self, ctx, msg_id):
		vote = Vote(self.bot)
		vote.grab_from_database(msg_id)
		msg = await self.get_vote_message(vote)
		res = await vote.result(msg)
		mes = f"https://ptb.discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{msg_id} \n"
		for k, v in res.items():
			mes += f"{k} = {v}\n"
		await ctx.respond(f"{mes}")

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