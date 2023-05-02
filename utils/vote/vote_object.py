import json
import datetime
import discord

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

class Vote:
	message_id = None
	name = None
	desc = None
	author = None
	options = None # де факто это не ролес а эможис, но мне в падлу переписывать БД
	whitelist = None
	endtime = None

	def __init__(self, bot):
		self.bot = bot

	def check_whitelist(self, role_id):
		if not self.whitelist:
			return 1
		
		if role_id not in self.whitelist.keys():
			return 0
		
		return self.whitelist[role_id]
		
	def parse_json(self, string):
		obj = json.loads(string)
		self.name = obj.get("name")
		self.desc = obj.get("desc")
		raw_options = obj.get("options")
		self.options = {}
		for k, v in raw_options.items():
			self.options[k.encode("utf-8")] = v
		self.whitelist = obj.get("whitelist")				
		self.endtime = datetime.datetime.fromtimestamp(obj.get("endtime"))

	async def send_message(self):
		if not self.options or not self.endtime:
			return
		emb = discord.Embed(title=self.name, description=self.desc, color=0xFF7F50)
		for k, v in self.options.items():
			emb.add_field(name=k.decode("utf-8"), value=v)

		emb.timestamp = self.endtime
		self.message_id = (await self.bot.get_guild(self.bot.config.bot["guild_id"]).get_channel(self.bot.config.channels["vote"]).send(embed=emb)).id

	async def result(self, msg):
		if not self.message_id:
			return
		if not msg:
			return
		winner = None
		second  = None
		result = {None: -100} # ha ha
		all_reactions = msg.reactions
		for r in all_reactions:
			if r not in self.options.keys():
				continue
			result[r] = 0
			async for u in r.users():		
				for rl in u.roles:
					result[r] += self.check_whitelist(rl.id)
			if result[r] > result[winner]:
				second = winner
				winner = r

		return result, winner, second

	def grab_from_database(self, msg_id):
		with self.bot.dbholder.interact() as cur:
			cur.execute(f"SELECT * FROM vote WHERE message_id = {msg_id}")
			data = cur.fetchone()
		
		if not data:
			return
		
		self.message_id = int(msg_id)
		self.name = data[1]
		self.desc = data[2]
		self.author = int(data[3])
		self.options = json.loads(data[4])
		self.whitelist = json.loads(data[5]) if data[5] else None
		self.endtime = datetime.datetime.fromtimestamp(float(data[6]))
	
	def upload_to_database(self):
		if not self.message_id:
			return False
		with self.bot.dbholder.interact() as cur:
			cur.execute(f"SELECT * FROM vote WHERE message_id = {self.message_id}")
			data = cur.fetchone()
			if data:
				return False
			ГИГАСТРОКА = f"INSERT INTO vote VALUES ('{self.message_id}', '{self.name}', '{self.desc}', '{self.author}', '{self.options}', '{self.whitelist}', '{self.endtime}')"
			cur.execute(ГИГАСТРОКА)
		return True