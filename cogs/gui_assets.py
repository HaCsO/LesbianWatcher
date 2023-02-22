import sqlite3
import discord
import json
import datetime

async def warn(author, user, logger, reason= "Не указана"):
	res, db, cur = get_structured_db_info(user)
	if res:
		dat = res[1]
		dat = json.loads(dat)
		dat[f"{res[2]+1}"] = {
			"moderator": f"{author.id}",
			"reason": reason,
			"datetime": f"{datetime.datetime.now().timestamp()}"
		}
		cur.execute(f"UPDATE warn SET additional = '{json.dumps(dat, ensure_ascii=False)}', warnamount = warnamount + 1 WHERE id = '{user.id}'")
	else:
		dat = {}
		dat["1"] = {
			"moderator": f"{author.id}",
			"reason": reason,
			"datetime": f"{datetime.datetime.now().timestamp()}"
		}
		cur.execute(f"INSERT INTO warn VALUES ('{user.id}', '{json.dumps(dat, ensure_ascii=False)}', 1)")

	db.commit()
	db.close()
	formats = [logger.UserFormatType({"AUTHOR": author, "USER": user})]
	emb = discord.Embed(title= "Варн", description=f"Пользователю {user.mention} было выдано наказание по причине:\n ```{reason}```", colour=0xff0000)
	await logger.log(msg= f"Пользователь AUTHOR выдал пользователю USER варн по причине: \"{reason}\"", embed= emb, formats= formats, is_punish= True, lock_discord_msg= True)

async def unwarn(author, user, logger, choosen_warn):
	if not choosen_warn:
		return None
	
	res, db, cur = get_structured_db_info(user)

	if not res:
		return None
	if res[2] <= 1:
		cur.execute(f"DELETE FROM warn WHERE id = {user.id}")
	else:
		dat = json.loads(res[1])
		sort_bin = {}
		for i in range(int(choosen_warn)+1, int(res[2])+1):
			sort_bin[str(i-1)] = dat[str(i)]
			del dat[str(i)]		
		del dat[choosen_warn]

		for k, v in sort_bin.items():
			dat[k] = v

		cur.execute(f"UPDATE warn SET additional = '{json.dumps(dat, ensure_ascii=False)}', warnamount = warnamount - 1 WHERE id = '{user.id}'")

	db.commit()
	db.close()
	reason = json.loads(res[1])[choosen_warn]["reason"]
	formats = [logger.UserFormatType({"AUTHOR": author, "USER": user})]
	emb = discord.Embed(title= "Варн", description=f"С пользователя {user.mention} был снят варн с причиной: ```{reason}```", colour=0x00ff00)
	await logger.log(msg= f"Пользователь AUTHOR снял с пользователя USER варн с причиной \"{reason}\"", embed= emb, formats= formats, is_punish= True, lock_discord_msg= True)
	return True

async def purge_warns(author, user, logger):
	res, db, cur = get_structured_db_info(user)
	if not res:
		return None
	
	cur.execute(f"DELETE FROM warn WHERE id = '{user.id}'")
	db.commit()
	db.close()
	formats = [logger.UserFormatType({"AUTHOR": author, "USER": user})]
	emb = discord.Embed(title= "Варн", description=f"С пользователя {user.mention} были сняты все варны", colour=0x00ff00)
	await logger.log(msg= f"Пользователь AUTHOR снял с пользователя USER все варны", embed= emb, formats= formats, is_punish= True, lock_discord_msg= True)

def get_structured_db_info(user):
	db = sqlite3.connect("data.db")
	cur = db.cursor()
	cur.execute(f"SELECT * FROM warn WHERE id = '{user.id}'")
	res = cur.fetchall()
	if not res:
		return None, db, cur
	return res[0], db, cur

class WarningWindow(discord.ui.Modal):
	def __init__(self, bot, verb, callback, *args, **kwargs):
		super().__init__(title=f"ВЫ УВЕРЕННЫ В: {verb}?")
		reason = discord.ui.InputText(label = "Напишите любой текст, для подтверждения", required=True, max_length=60)
		self.add_item(reason)
		self.bot = bot
		self.cb = callback
		self.cb_args = args
		self.cb_kwargs = kwargs

	async def callback(self, interaction: discord.Interaction):
		await self.cb(*self.cb_args, **self.cb_kwargs)
		await interaction.response.defer()


class WarnCard(discord.ui.View):
	def __init__(self, user, author, bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.timeout = 60
		self.user = user
		self.bot = bot
		self.author = author
		self.choosen_warn = None
		self.message_cache = None
		self.update_view_options()

	async def interaction_check(self, interaction: discord.Interaction) -> bool:
		return interaction.user == self.author

	async def on_timeout(self):
		if self.message_cache:
			await self.message_cache.delete()
		return await super().on_timeout()

	async def on_error(self, error: Exception, item, interaction: discord.Interaction):
		return await super().on_error(error, item, interaction)

	@discord.ui.button(label="Окончить", style=discord.ButtonStyle.red)
	async def button_stop(self, button, interaction):
		await interaction.message.delete()
		self.stop()

	@discord.ui.button(label="Выдать варн", style=discord.ButtonStyle.blurple)
	async def button_warn(self, button, interaction:discord.Interaction):
		self.message_cache = interaction.message
		await interaction.response.send_modal(WarnGiveView(self.bot, self))

	@discord.ui.button(label="Снять варн", style=discord.ButtonStyle.green)
	async def button_unwarn(self, button, interaction):
		self.message_cache = interaction.message
		if await unwarn(self.author, self.user, self.bot.logger, self.choosen_warn):
			self.choosen_warn = None
		await interaction.response.edit_message(embed= self.update_embed(), view= self)

	@discord.ui.button(label="Снять все варны", style=discord.ButtonStyle.secondary)
	async def button_purge_warns(self, button, interaction):
		self.message_cache = interaction.message
		await purge_warns(self.author, self.user, self.bot.logger)
		await interaction.response.edit_message(embed= self.update_embed(), view= self)

	@discord.ui.select(placeholder="Выберите варн")
	async def select_callback(self, select, interaction):
		self.choosen_warn = select.values[0]
		await interaction.response.edit_message(embed= self.update_embed(), view= self)


	def update_embed(self):
		res, db, cur = get_structured_db_info(self.user)
		db.close()
		warnlist = None
		if res and int(res[2]):
			dat = json.loads(res[1])
			self.update_view_options(dat)
			warnlist = ""
			for k, v in dat.items():
				warnlist += f"[{datetime.datetime.fromtimestamp(float(v['datetime']))}] **{k}**: <@!{v['moderator']}> - ```{v['reason']}```\n"
		else:
			self.update_view_options()
			
		emb = discord.Embed(title=f"{self.user.name}", description= warnlist if warnlist else "Этот человек слишком хорошо для этого мира...", color=0xFFFF00)
		emb.set_thumbnail(url= self.user.avatar.url)
		emb.set_footer(text=f"Выбранный варн для снятия: {'номер ' + self.choosen_warn if self.choosen_warn else 'не выбран'}")
		return emb

	def update_view_options(self, warns= None):
		if not warns:
			res, db, cur = get_structured_db_info(self.user)
			if not res:
				self.remove_item(self.select_callback)
				return
			warns = json.loads(res[1])
			db.close()

		self.select_callback.options = []
		for i in warns.keys():
			self.select_callback.add_option(label= f"варн номер {i[0]}", value=i[0], description=warns[i[0]]["reason"])

		if self.select_callback not in self.children:
			self.add_item(self.select_callback)
		return True


class WarnGive(discord.ui.Modal):
	def __init__(self, bot, author, user, msg= None):
		super().__init__(title="Выдать варн")
		reason = discord.ui.InputText(label = "Введите причину", required=True, max_length=60)
		self.add_item(reason)
		self.bot = bot
		self.author = author
		self.user = user
		self.msg = msg

	async def interact(self, interaction):
		await interaction.response.defer()

	async def callback(self, interaction: discord.Interaction):
		user = self.user
		author = self.author
		logger = self.bot.logger
		await warn(author, user, logger, interaction.data['components'][0]['components'][0]['value'])
		if self.msg:
			await self.msg.delete()

		await self.interact(interaction)

class WarnGiveView(WarnGive):
	def __init__(self, bot, view):
		super().__init__(bot, view.author, view.user)
		self.view

	async def interact(self, interaction):
		await interaction.response.edit_message(embed= self.view.update_embed(), view= self.view)
	