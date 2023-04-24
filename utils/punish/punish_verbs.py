import sqlite3
import discord
import json
import datetime

class Punish():
	def __init__(self, author, user, bot):
		self.author = author
		self.user = user
		self.bot = bot

	async def warn(self, reason= "Не указана"):
		with self.bot.dbholder.interact() as cur:
			res = cur.get_structured_db_info(self.user)
			if res:
				dat = res[1]
				dat = json.loads(dat)
				dat[f"{res[2]+1}"] = {
					"moderator": f"{self.author.id}",
					"reason": reason,
					"datetime": f"{datetime.datetime.now().timestamp()}"
				}
				cur.execute(f"UPDATE warn SET additional = '{json.dumps(dat, ensure_ascii=False)}', warnamount = warnamount + 1 WHERE id = '{self.user.id}'")
				if int(res[2]+1) == 2 and not len(json.loads(res[3])):
					await self.mime("2 активных варна")
				elif int(res[2]+1) >= 3 and not len(json.loads(res[4])):
					await self.clown("3 активных варна")
			else:
				dat = {}
				dat["1"] = {
					"moderator": f"{self.author.id}",
					"reason": reason,
					"datetime": f"{datetime.datetime.now().timestamp()}"
				}
				empty_json = "{}"
				cur.execute(f"INSERT INTO warn VALUES ('{self.user.id}', '{json.dumps(dat, ensure_ascii=False)}', 1, '{empty_json}', '{empty_json}')")

		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user}), self.bot.logger.BaseFormat({"REASON": reason})]
		await self.bot.logger.log_localised("warn", formats= formats, user=self.user.mention, reason=reason)

	async def unwarn(self, choosen_warn):
		if not choosen_warn:
			return None
		
		with self.bot.dbholder.interact() as cur:
			res = cur.get_structured_db_info(self.user)

			if not res:
				return None
			if res[2] <= 1:
				empty_json = "{}"
				cur.execute(f"UPDATE warn SET additional = '{empty_json}', warnamount = 0 WHERE id = '{self.user.id}'")
			else:
				dat = json.loads(res[1])
				sort_bin = {}
				for i in range(int(choosen_warn)+1, int(res[2])+1):
					sort_bin[str(i-1)] = dat[str(i)]
					del dat[str(i)]		
				del dat[choosen_warn]

				for k, v in sort_bin.items():
					dat[k] = v

				cur.execute(f"UPDATE warn SET additional = '{json.dumps(dat, ensure_ascii=False)}', warnamount = warnamount - 1 WHERE id = '{self.user.id}'")
		reason = json.loads(res[1])[choosen_warn]["reason"]
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user}), self.bot.logger.BaseFormat({"REASON": reason})]
		await self.bot.logger.log_localised("unwarn", formats= formats, user=self.user.mention, reason=reason)
		return True

	
	async def purge_warns(self):
		with self.bot.dbholder.interact() as cur:
			res = cur.get_structured_db_info(self.user)
			if not res:
				return None
			
			empty_json = "{}"
			cur.execute(f"UPDATE warn SET additional = '{empty_json}', warnamount = 0 WHERE id = '{self.user.id}'")
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user})]
		await self.bot.logger.log_localised("purgewarns", formats= formats, user=self.user.mention)

	async def mime(self, reason):
		role_id = self.bot.config.roles["mime"]
		if not role_id:
			await self.bot.logger.log_localised("role_not_found")
			return None
		
		try:
			role = self.bot.get_guild(self.bot.guild_id).get_role(role_id)
		except:
			await self.bot.logger.log_localised("role_not_found")
			return None

		with self.bot.dbholder.interact() as cur:
			res = cur.get_structured_db_info(self.user)
			if not res:
				dat = {}
				dat = {
					"moderator": f"{self.author.id}",
					"reason": reason,
					"datetime": f"{datetime.datetime.now().timestamp()}"
				}
				empty_json = "{}"
				cur.execute(f"INSERT INTO warn VALUES ('{self.user.id}', '{empty_json}', 0, '{json.dumps(dat, ensure_ascii=False)}', '{empty_json}')")

			else:
				dat = json.loads(res[3])
				if len(dat):
					return None

				dat = {
					"moderator": f"{self.author.id}",
					"reason": reason,
					"datetime": f"{datetime.datetime.now().timestamp()}"
				}
				cur.execute(f"UPDATE warn SET mime = '{json.dumps(dat, ensure_ascii=False)}' WHERE id = '{self.user.id}'")

		await self.user.add_roles(role)
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user}), self.bot.logger.BaseFormat({"REASON": reason})]
		await self.bot.logger.log_localised("give_mime", formats= formats, user= self.user.mention, reason=reason)
		return True

	async def clown(self, reason):
		role_id = self.bot.config.roles["clown"]
		if not role_id:
			await self.bot.logger.log_localised("role_not_found")
			return None
		
		try:
			role = self.bot.get_guild(self.bot.guild_id).get_role(role_id)
		except:
			await self.bot.logger.log_localised("role_not_found")
			return None

		with self.bot.dbholder.interact() as cur:
			res = cur.get_structured_db_info(self.user)

			if not res:
				dat = {}
				dat = {
					"moderator": f"{self.author.id}",
					"reason": reason,
					"datetime": f"{datetime.datetime.now().timestamp()}"
				}
				empty_json = "{}"
				cur.execute(f"INSERT INTO warn VALUES ('{self.user.id}', '{empty_json}', 0, '{empty_json}', '{json.dumps(dat, ensure_ascii=False)}')")

			else:
				dat = json.loads(res[4])
				if len(dat):
					return None

				dat = {
					"moderator": f"{self.author.id}",
					"reason": reason,
					"datetime": f"{datetime.datetime.now().timestamp()}"
				}
				cur.execute(f"UPDATE warn SET clown = '{json.dumps(dat, ensure_ascii=False)}' WHERE id = '{self.user.id}'")

		await self.user.add_roles(role)
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user}), self.bot.logger.BaseFormat({"REASON": reason})]
		await self.bot.logger.log_localised("give_clown", formats= formats, user= self.user.mention, reason=reason)
		await self.bot.warn_headmod_about_clown(self.user)
		return True

	async def unmime(self):
		role_id = self.bot.config.roles["mime"]
		if not role_id:
			await self.bot.logger.log_localised("role_not_found")
			return None
		
		try:
			role = self.bot.get_guild(self.bot.guild_id).get_role(role_id)
		except:
			await self.bot.logger.log_localised("role_not_found")
			return None

		with self.bot.dbholder.interact() as cur:
			res = cur.get_structured_db_info(self.user)

			if not res:
				return None
			if not len(json.loads(res[3])):
				return None

			dat = {}
			cur.execute(f"UPDATE warn SET mime = '{dat}' WHERE id = '{self.user.id}'")

		await self.user.remove_roles(role)
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user})]
		await self.bot.logger.log_localised("unmime", formats= formats, user= self.user.mention)
		return True

	async def unclown(self):
		role_id = self.bot.config.roles["clown"]
		if not role_id:
			await self.bot.logger.log_localised("role_not_found")
			return None
		
		try:
			role = self.bot.get_guild(self.bot.guild_id).get_role(role_id)
		except:
			await self.bot.logger.log_localised("role_not_found")
			return None

		with self.bot.dbholder.interact() as cur:
			res = cur.get_structured_db_info(self.user)

			if not res:
				return None
			if not len(json.loads(res[4])):
				return None

			dat = {}
			cur.execute(f"UPDATE warn SET clown = '{dat}' WHERE id = '{self.user.id}'")

		await self.user.remove_roles(role)
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user})]
		await self.bot.logger.log_localised("unclown", formats= formats, user= self.user.mention)
		return True
