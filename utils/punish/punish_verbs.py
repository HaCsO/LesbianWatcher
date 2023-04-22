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
		with self.bot.dbhandler.interact() as cur:
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
				elif int(res[2]+1) >= 4 and not len(json.loads(res[4])):
					await self.clown("4 активных варна")
			else:
				dat = {}
				dat["1"] = {
					"moderator": f"{self.author.id}",
					"reason": reason,
					"datetime": f"{datetime.datetime.now().timestamp()}"
				}
				empty_json = "{}"
				cur.execute(f"INSERT INTO warn VALUES ('{self.user.id}', '{json.dumps(dat, ensure_ascii=False)}', 1, '{empty_json}', '{empty_json}')")

		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user})]
		emb = discord.Embed(title= "Варн", description=f"Пользователю {self.user.mention} было выдано наказание по причине:\n ```{reason}```", colour=0x671515)
		await self.bot.logger.log(msg= f"Пользователь AUTHOR выдал пользователю USER варн по причине: \"{reason}\"", embed= emb, formats= formats, is_punish= True, lock_discord_msg= True)

	async def unwarn(self, choosen_warn):
		if not choosen_warn:
			return None
		
		with self.bot.dbhandler.interact() as cur:
			res = cur.get_structured_db_info(self.user)

			if not res:
				return None
			if res[2] <= 1:
				# cur.execute(f"DELETE FROM warn WHERE id = {self.user.id}")
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
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user})]
		emb = discord.Embed(title= "Варн", description=f"С пользователя {self.user.mention} был снят варн с причиной: ```{reason}```", colour=0x0099ff)
		await self.bot.logger.log(msg= f"Пользователь AUTHOR снял с пользователя USER варн с причиной \"{reason}\"", embed= emb, formats= formats, is_punish= True, lock_discord_msg= True)
		return True

	
	async def purge_warns(self):
		with self.bot.dbhandler.interact() as cur:
			res = cur.get_structured_db_info(self.user)
			if not res:
				return None
			
			empty_json = "{}"
			cur.execute(f"UPDATE warn SET additional = '{empty_json}', warnamount = 0 WHERE id = '{self.user.id}'")
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user})]
		emb = discord.Embed(title= "Варн", description=f"С пользователя {self.user.mention} были сняты все варны", colour=0x0099ff)
		await self.bot.logger.log(msg= f"Пользователь AUTHOR снял с пользователя USER все варны", embed= emb, formats= formats, is_punish= True, lock_discord_msg= True)

	async def mime(self, reason):
		role_id = self.bot.config.roles["mime"]
		if not role_id:
			await self.bot.logger.log(f"{self.author.mention} Внимание, не обнаружена роль мима. Проверьте конфигурацию!")
			return None
		
		try:
			role = self.bot.get_guild(self.bot.guild_id).get_role(role_id)
		except:
			await self.bot.logger.log(f"{self.author.mention} Внимание, не обнаружена роль мима. Проверьте конфигурацию!")
			return None

		with self.bot.dbhandler.interact() as cur:
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
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user})]
		emb = discord.Embed(title= "Мим", description=f"Пользователю {self.user.mention} был выдан мим по причине:\n```{reason}```", colour=0x671515)
		await self.bot.logger.log(msg= f"Пользователь AUTHOR выдал пользователю USER мима по причине '{reason}'", embed= emb, formats= formats, is_punish= True, lock_discord_msg= True)
		return True

	async def clown(self, reason):
		role_id = self.bot.config.roles["clown"]
		if not role_id:
			await self.bot.logger.log(f"{self.author.mention} Внимание, не обнаружена роль клоуна. Проверьте конфигурацию!")
			return None
		
		try:
			role = self.bot.get_guild(self.bot.guild_id).get_role(role_id)
		except:
			await self.bot.logger.log(f"{self.author.mention} Внимание, не обнаружена роль клоуна. Проверьте конфигурацию!")
			return None

		with self.bot.dbhandler.interact() as cur:
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
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user})]
		emb = discord.Embed(title= "Клоун", description=f"Пользователю {self.user.mention} был выдан клоун по причине:\n```{reason}```", colour=0x671515)
		await self.bot.logger.log(msg= f"Пользователь AUTHOR выдал пользователю USER клоуна по причине '{reason}'", embed= emb, formats= formats, is_punish= True, lock_discord_msg= True)
		if self.bot.config.channels["talk"]:
			emb = discord.Embed(title="Клоун", description=f"Пользователь {self.user.mention} получил статус клоуна. Рекомендуется полная его блокировка!", color=0xff0000)
			await self.bot.get_channel(self.bot.config.channels["talk"]).send(f"<@!{self.bot.config.users['headmod']}>", embed= emb)
		return True

	async def unmime(self):
		role_id = self.bot.config.roles["mime"]
		if not role_id:
			await self.bot.logger.log(f"{self.author.mention} Внимание, не обнаружена роль мима. Проверьте конфигурацию!")
			return None
		
		try:
			role = self.bot.get_guild(self.bot.guild_id).get_role(role_id)
		except:
			await self.bot.logger.log(f"{self.author.mention} Внимание, не обнаружена роль мима. Проверьте конфигурацию!")
			return None

		with self.bot.dbhandler.interact() as cur:
			res = cur.get_structured_db_info(self.user)

			if not res:
				return None
			if not len(json.loads(res[3])):
				return None

			dat = {}
			cur.execute(f"UPDATE warn SET mime = '{dat}' WHERE id = '{self.user.id}'")

		await self.user.remove_roles(role)
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user})]
		emb = discord.Embed(title= "Мим", description=f"С пользователя {self.user.mention} был снят мим", colour=0x0099ff)
		await self.bot.logger.log(msg= f"Пользователь AUTHOR снял с пользователя USER мима", embed= emb, formats= formats, is_punish= True, lock_discord_msg= True)
		return True

	async def unclown(self):
		role_id = self.bot.config.roles["clown"]
		if not role_id:
			await self.bot.logger.log(f"{self.author.mention} Внимание, не обнаружена роль мима. Проверьте конфигурацию!")
			return None
		
		try:
			role = self.bot.get_guild(self.bot.guild_id).get_role(role_id)
		except:
			await self.bot.logger.log(f"{self.author.mention} Внимание, не обнаружена роль мима. Проверьте конфигурацию!")
			return None

		with self.bot.dbhandler.interact() as cur:
			res = cur.get_structured_db_info(self.user)

			if not res:
				return None
			if not len(json.loads(res[4])):
				return None

			dat = {}
			cur.execute(f"UPDATE warn SET clown = '{dat}' WHERE id = '{self.user.id}'")

		await self.user.remove_roles(role)
		formats = [self.bot.logger.UserFormatType({"AUTHOR": self.author, "USER": self.user})]
		emb = discord.Embed(title= "Клоун", description=f"С пользователя {self.user.mention} был снят клоун", colour=0x0099ff)
		await self.bot.logger.log(msg= f"Пользователь AUTHOR снял с пользователя USER клоуна", embed= emb, formats= formats, is_punish= True, lock_discord_msg= True)
		return True
