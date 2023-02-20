import sqlite3
import discord
import json
import datetime

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
		await interaction.response.send_modal(WarnGive(self.bot, self))

	@discord.ui.button(label="Снять варн", style=discord.ButtonStyle.green)
	async def button_unwarn(self, button, interaction):
		self.message_cache = interaction.message
		self.unwarn()
		await interaction.response.edit_message(embed= self.update_embed(), view= self)

	@discord.ui.button(label="Снять все варны", style=discord.ButtonStyle.secondary)
	async def button_purge_warns(self, button, interaction):
		self.message_cache = interaction.message
		self.purge_warns()
		await interaction.response.edit_message(embed= self.update_embed(), view= self)

	@discord.ui.select(placeholder="Выберите варн")
	async def select_callback(self, select, interaction):
		self.choosen_warn = select.values[0]
		await interaction.response.edit_message(embed= self.update_embed(), view= self)


	def update_embed(self):
		res, db, cur = self.get_structured_db_info()
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
			res, db, cur = self.get_structured_db_info()
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

	def warn(self, reason= "Не указана"):
		res, db, cur = self.get_structured_db_info()
		if res:
			dat = res[1]
			dat = json.loads(dat)
			dat[f"{res[2]+1}"] = {
				"moderator": f"{self.author.id}",
				"reason": reason,
				"datetime": f"{datetime.datetime.now().timestamp()}"
			}
			cur.execute(f"UPDATE warn SET additional = '{json.dumps(dat, ensure_ascii=False)}', warnamount = warnamount + 1 WHERE id = '{self.user.id}'")
		else:
			dat = {}
			dat["1"] = {
				"moderator": f"{self.author.id}",
				"reason": reason,
				"datetime": f"{datetime.datetime.now().timestamp()}"
			}
			cur.execute(f"INSERT INTO warn VALUES ('{self.user.id}', '{json.dumps(dat, ensure_ascii=False)}', 1)")

		db.commit()
		db.close()

	def unwarn(self):
		if not self.choosen_warn:
			return None
		
		res, db, cur = self.get_structured_db_info()

		if not res:
			return None
		
		if res[2] <= 1:
			cur.execute(f"DELETE FROM warn WHERE id = {self.user.id}")
		else:
			dat = json.loads(res[1])
			sort_bin = {}
			for i in range(int(self.choosen_warn)+1, int(res[2])+1):
				sort_bin[str(i-1)] = dat[str(i)]
				del dat[str(i)]		
			del dat[self.choosen_warn]

			for k, v in sort_bin.items():
				dat[k] = v

			cur.execute(f"UPDATE warn SET additional = '{json.dumps(dat, ensure_ascii=False)}', warnamount = warnamount - 1 WHERE id = '{self.user.id}'")

		db.commit()
		db.close()
		self.choosen_warn = None
		return True

	def purge_warns(self):
		res, db, cur = self.get_structured_db_info()
		if not res:
			return None
		
		cur.execute(f"DELETE FROM warn WHERE id = '{self.user.id}'")
		db.commit()
		db.close()
	
	def get_structured_db_info(self):
		db = sqlite3.connect("data.db")
		cur = db.cursor()
		cur.execute(f"SELECT * FROM warn WHERE id = '{self.user.id}'")
		res = cur.fetchall()
		if not res:
			return None, db, cur
		return res[0], db, cur
		

class WarnGive(discord.ui.Modal):
	def __init__(self, bot, view):
		super().__init__(title="Выдать варн")
		reason = discord.ui.InputText(label = "Введите причину", required=True, max_length=60)
		self.add_item(reason)
		self.bot = bot
		self.view = view

	async def callback(self, interaction: discord.Interaction):
		self.view.warn(interaction.data['components'][0]['components'][0]['value'])
		await interaction.response.edit_message(embed= self.view.update_embed(), view= self.view)
