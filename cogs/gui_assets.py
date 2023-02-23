import discord
import json
import datetime
from .punish_verbs import *

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
		self.warnmodel = Punish(author, user, bot)

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
		if await self.warnmodel.unwarn(self.choosen_warn):
			self.choosen_warn = None
		await interaction.response.edit_message(embed= self.update_embed(), view= self)

	@discord.ui.button(label="Снять все варны", style=discord.ButtonStyle.secondary)
	async def button_purge_warns(self, button, interaction):
		self.message_cache = interaction.message
		await self.warnmodel.purge_warns()
		await interaction.response.edit_message(embed= self.update_embed(), view= self)

	@discord.ui.select(placeholder="Выберите варн")
	async def select_callback(self, select, interaction):
		self.choosen_warn = select.values[0]
		await interaction.response.edit_message(embed= self.update_embed(), view= self)


	def update_embed(self):
		res, db, cur = get_structured_db_info(self.user)
		db.close()
		warnlist = None
		if res:
			warnlist = ""
			dat = json.loads(res[3])
			if len(dat):
				warnlist += "**Этот человек МИМ!**\n"

			dat = json.loads(res[4])
			if len(dat):
				warnlist += "**Этот человек КЛОУН!**\n"

			dat = json.loads(res[1])
			self.update_view_options(dat)
				
			if int(res[2]):
				warnlist += "**Варны:\n**"
				for k, v in dat.items():
					warnlist += f"[{datetime.datetime.fromtimestamp(float(v['datetime']))}] **{k}**: <@!{v['moderator']}> - ```{v['reason']}```\n"
		else:
			self.update_view_options()
			
		emb = discord.Embed(title=f"{self.user.name}", description= warnlist if warnlist else "Этот человек слишком хорошо для этого мира...", color=0xffa586)
		emb.set_thumbnail(url= self.user.avatar.url)
		emb.set_footer(text=f"Выбранный варн для снятия: {'номер ' + self.choosen_warn if self.choosen_warn else 'не выбран'}")
		return emb

	def update_view_options(self, warns= None):
		if not warns:
			res, db, cur = get_structured_db_info(self.user)
			db.close()
			if not res:
				self.remove_item(self.select_callback)
				return
			warns = json.loads(res[1])
			if len(warns) < 1:
				self.remove_item(self.select_callback)
				return

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
		warn = Punish(author, user, self.bot)
		await warn.warn(interaction.data['components'][0]['components'][0]['value'])
		if self.msg:
			await self.msg.delete()

		await self.interact(interaction)

class WarnGiveView(WarnGive):
	def __init__(self, bot, view):
		super().__init__(bot, view.author, view.user)
		self.view = view

	async def interact(self, interaction):
		await interaction.response.edit_message(embed= self.view.update_embed(), view= self.view)
	