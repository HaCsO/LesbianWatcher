import sqlite3
import json
import datetime
import discord

"""
data object tree

{
	"name": "huy"
	"emoji": {
		"emoji_id1 || emoji1": "result1",
		"emoji_id2 || emoji1": "result2",
		...
	},
	"whitelist": [
		role_id1,
		role_id2,
		...
	],
	"weight": {
		"role_id1": int_weight1,
		"role_id2": int_weight2,
		...
	}
}
"""

emoji_list = [
	"0️⃣",
	"1️⃣",
	"2️⃣",
	"3️⃣",
	"4️⃣",
	"5️⃣",
	"6️⃣",
	"7️⃣",
	"8️⃣",
	"9️⃣",
	"🔟"
]

class VoteType():
	def __init__(self, bot):
		self.bot = bot
		self.msg_id: int = None
		self.endtime: datetime.datetime = None
		self.data: dict = {
			"name": None,
			"emoji": {},
			"whitelist": {},
			"weight": {}
		}
		self.author: discord.Member = None

	def set_yon(self):
		self.data["emoji"] = {
			"✅": "Да",
			"❌": "Нет"
		}

	async def start_vote(self, ctx):
		desc = f"**{self.data['name']}**\n"
		for emoji, value in self.data["emoji"].items():
			desc += f"{emoji}: {value}\n"
		emb = discord.Embed(title="Голосование", description=desc, color=0xffa586)
		emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
		emb.set_footer(value="Внимание, если вы выберете больше одной реакции то ваш голос учитываться не будет!")
		msg = await ctx.send(embed=emb)
		for emoji in self.data["emoji"].keys():
			await msg.add_reaction(emoji)
		self.msg_id = msg.id
		self.upload_to_db()

	def add_options(self, options):
		for n, v in enumerate(options):
			self.data["emoji"][emoji_list[n]] = v

	def check_end(self, time: datetime.datetime=None):
		return True if not time else time > self.endtime

	def upload_to_db(self):
		db = sqlite3.connect("data.db")
		cur = db.cursor()
		cur.execute(f"SELECT * FROM vote WHERE message_id = '{self.msg_id}'")
		res = cur.fetchone()
		if(res):
			cur.execute(f"UPDATE vote SET message_id ='{self.msg_id}', author = '{self.author.id}', additional = '{json.dumps(self.data, ensure_ascii=False)}', endtime = '{self.endtime.timestamp()}') WHERE message_id = {self.msg_id}")
		else:
			cur.execute(f"INSERT INTO vote VALUES ('{self.msg_id}', '{self.author.id}', '{json.dumps(self.data, ensure_ascii=False)}', '{self.endtime.timestamp()}')")
			if(self.msg_id != None):
				cur.execute(f"DELETE FROM vote WHERE message_id = 'None' AND additional = '{json.dumps(self.data, ensure_ascii=False)}'")
		db.commit()
		db.close()

	def grab_from_db(self, id):
		db = sqlite3.connect("data.db")
		cur = db.cursor()
		cur.execute(f"SELECT * FROM vote WHERE message_id = '{id}'")
		res = cur.fetchone()
		db.close()
		if not res:
			return None
		
		self.msg_id = id
		self.endtime = datetime.datetime.fromtimestamp(float(res[3]))
		self.data = json.loads(res[2])
		try:
			self.author = self.bot.get_guild(self.bot.guild_id).get_member(int(res[1]))
		except:
			self.author = None

		return True
	
	def fill_from_data(self, msg_id, endtime, author, data):
		self.msg_id = msg_id
		try:
			self.author = self.bot.get_guild(self.bot.guild_id).get_member(author)
		except:
			self.author = None
		self.endtime = datetime.datetime.fromtimestamp(endtime)
		self.data = json.loads(data)

