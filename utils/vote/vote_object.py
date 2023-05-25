import json
import datetime
import discord
import emoji

class Vote:
	message_id = None
	name = None
	desc = None
	author = None
	options = None # де факто это не ролес а эможис, но мне в падлу переписывать БД
	whitelist = None
	endtime = None
	mentions = None

	def __init__(self, bot):
		self.bot = bot

	def check_whitelist(self, role_id):
		if not self.whitelist:
			return 1
		
		if str(role_id) not in self.whitelist.keys():
			return 0

		return self.whitelist[str(role_id)]

	def get_mentions_str(self):
		if not self.mentions:
			return None
		ments = ""
		for u in self.mentions:
			ments += f"{u}\n"
		return ments

	async def send_message(self):
		if not self.options or not self.endtime:
			return

		ments = self.get_mentions_str()
		emb = discord.Embed(title=self.name, description=self.desc, color=0xFF7F50)
		for k, v in self.options.items():
			emb.add_field(name=emoji.emojize(k, language="alias"), value=v, inline= False)

		emb.timestamp = datetime.datetime.fromtimestamp(self.endtime)
		msg = await self.bot.get_channel_by_known_guild(self.bot.config.channels["vote"]).send(ments, embed=emb)
		self.message_id = msg.id
		for k in self.options.keys():
			await msg.add_reaction(emoji.emojize(k, language="alias"))

	async def edit_message_to_final(self, msg):
		if not self.message_id or self.message_id != msg.id:
			return
		res = await self.result(msg)
		rres = ""
		maxv = None
		maxb = 0
		for k, v in res.items():
			rres += f"{k} = *{v}* **баллов**\n"
			if maxb <= v:
				maxv = k
		rres += f"\n**Победитель:**\n{maxv}: {self.options[maxv]}"
		emb = discord.Embed(title=self.name, description=self.desc + f"\n\n**Результат голосования**: \n{rres}", color=0xFF7F50)
		await msg.clear_reactions()
		await msg.edit(embed=emb)

	async def result(self, msg):
		if not self.message_id:
			return
		if not msg:
			return
		result = {}
		all_reactions = msg.reactions
		collisions = {}
		for r in all_reactions:
			emo = emoji.EMOJI_DATA[r.emoji]["alias"][0]
			if emo not in self.options.keys():
				continue
			result[emo] = 0
			collisions[emo] = {}
			async for u in r.users():
				r = 0
				for rl in u.roles:
					r = max(self.check_whitelist(rl.id), r)

				if r < 1 and "everyone" in self.whitelist.keys():
					r = self.whitelist["everyone"]

				if r:
					collisions[emo][u.id] = r
				result[emo] += r
		result = self.check_collisions(collisions, result)
		return result
	
	def check_collisions(self, col, res):
		keys = list(col.keys())
		for n, k in enumerate(keys):
			p_users = list(col[k].keys())
			rem = []
			for j in range(n+1, len(keys)):
				for u in list(col[keys[j]]):
					if u in p_users:
						rem.append(u)
						res[keys[j]] -= col[keys[j]][u]
			if rem:
				for u in rem:
					res[k] -= col[k][u]
		return res

	def check_done(self):
		return datetime.datetime.fromtimestamp(self.endtime) < datetime.datetime.now() if self.endtime else False

	def parse_json(self, string):
		obj = json.loads(string)
		self.mentions = obj.get("mentions")
		self.name = obj.get("name")
		self.desc = obj.get("desc")
		# self.options = obj.get("options")
		raw_options = obj.get("options")
		self.options = {}
		for k, v in raw_options.items():
			self.options[emoji.EMOJI_DATA[k]["alias"][0]] = v
		self.whitelist = obj.get("whitelist")				
		self.endtime = obj.get("endtime")

	def grab_from_database(self, msg_id):
		with self.bot.dbholder.interact() as cur:
			cur.execute(f"SELECT * FROM vote WHERE message_id = {msg_id}")
			data = cur.fetchone()
		
		if not data:
			return
		
		self.message_id = int(msg_id)
		self.mentions = json.loads(data[1].replace("'", "\"")) if data[1] != "None" else None
		self.name = data[2]
		self.desc = data[3]
		self.author = int(data[4])
		self.options = json.loads(data[5].replace("'", "\""))
		self.whitelist = json.loads(data[6].replace("'", "\"")) if data[6] != "None" else None
		self.endtime = float(data[7])
	
	def upload_to_database(self):
		if not self.message_id:
			return False
		with self.bot.dbholder.interact() as cur:
			cur.execute(f"SELECT * FROM vote WHERE message_id = {self.message_id}")
			data = cur.fetchone()
			if data:
				return False
			ГИГАСТРОКА = f'INSERT INTO vote VALUES ("{self.message_id}", "{self.mentions}", "{self.name}", "{self.desc}", "{self.author}", "{self.options}", "{self.whitelist}", "{self.endtime}")'
			cur.execute(ГИГАСТРОКА)
		return True
	
	def remove_from_db(self):
		if not self.message_id:
			return False
		with self.bot.dbholder.interact() as cur:
			cur.execute(f"DELETE FROM vote WHERE message_id = {self.message_id}")
