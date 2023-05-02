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
	author = None
	roles = None # де факто это не ролес а эможис, но мне в падлу переписывать БД
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
			if r not in self.roles.keys():
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
		self.author = int(data[1])
		self.roles = json.loads(data[2])
		self.whitelist = json.loads(data[3]) if data[3] else None
		self.endtime = datetime.datetime.fromtimestamp(float(data[4]))
	
	def upload_to_database(self):
		if not self.message_id:
			return False
		with self.bot.dbholder.interact() as cur:
			cur.execute(f"SELECT * FROM vote WHERE message_id = {self.message_id}")
			data = cur.fetchone()
			if data:
				return False
			cur.execute(f"INSERT INTO vote VALUES ('{self.message_id}', '{self.author}', '{self.roles}', '{self.whitelist}', '{self.endtime}')")
		return True