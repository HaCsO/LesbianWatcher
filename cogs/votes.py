import discord
from discord.ext import commands, tasks
import sqlite3
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
		
	async def choose_vote(self, ctx: commands.Context, only_not_posted= False):
		await ctx.defer()
		await self.get_all_votes()
		votes = []
		vote_msg = ""
		listofvotes = self.fetchet_votes.values() if not only_not_posted else [vote for key, vote in self.fetchet_votes.items() if key == None]
		if not len(listofvotes):
			await ctx.respond("Не обнаружено!")
			return
		
		for n, vote in enumerate(listofvotes):
			vote_msg += f"{n+1}:{vote.data['name']}\n"
			votes.append(vote)
		await ctx.send(f"Пожалуйста, отправте следующим сообщением один из номеров возможных голосований для выбора:\n{vote_msg}")

		def check(m):
			return m.author == ctx.author

		vote = await self.bot.wait_for("message", check=check)
		try:
			votenum = int(vote.content)
		except:
			await ctx.respond("Введено не верное число!")
			return False

		await vote.delete()
		await ctx.respond(f"Выбран варн под номером: {votenum}!")
		return votes[votenum-1]

	@is_staff()
	@commands.slash_command()
	async def create_vote(self, ctx, name: str, options: discord.Option(str, "Введите возможные варианты ответа через (;). Изначально: Да;Нет.", required= False)):
		vote = VoteType(self.bot)
		vote.data["name"] = name
		vote.author = ctx.author
		vote.endtime = datetime.datetime.now() + datetime.timedelta(days=1)
		if(not options):
			vote.set_yon()
		else:
			opti = options.split(";")
			if(len(opti) > 10):
				await ctx.respond("Превышено количество допустимых вариантов ответа!")
				return
			vote.add_options(opti)

		vote.upload_to_db()
		await self.get_all_votes()
		await ctx.respond("Готово!")

	@is_staff()
	@commands.slash_command()
	async def start_vote(self, ctx):
		vote = await self.choose_vote(ctx, True)
		if(not vote):
			return
		
		await vote.start_vote(ctx)

	async def get_all_votes(self):
		db = sqlite3.connect("data.db")
		cur = db.cursor()
		cur.execute(f"SELECT * FROM vote")
		res = cur.fetchall()
		db.close()
		for votes in self.fetchet_votes.values():
			del votes
		self.fetchet_votes = {}
		for i in res:
			vote = VoteType(self.bot)
			voteid = None
			if i[0] != "None":
				voteid = i[0]
				vote.grab_from_db(voteid)
			else:
				vote.fill_from_data(i[0], float(i[3]), int(i[1]), i[2])
			self.fetchet_votes[voteid] = vote


def setup(bot):
	bot.add_cog(Votes(bot))
	print("[Lesbian Wathcer] votes engaged!")