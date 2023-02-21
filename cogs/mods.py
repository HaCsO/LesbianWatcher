import discord
from discord.ext import commands
import sqlite3
import json
import datetime
from .gui_assets import *

# additional data structure in db

# warns
# 	moderator
# 	reason
# 	datetime
# unwarns
# 	moderator
# 	reason
# 	datetime
class Mods(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def is_moderator():
		def predicate(ctx):
			mods = ctx.bot.config.config["moders"]
			return ctx.author.id in mods
		return commands.check(predicate)
	
	def is_owner():
		def predicate(ctx):
			return ctx.author.id == ctx.bot.config.config["owner"]
		return commands.check(predicate)
	
	def is_headmod():
		def predicate(ctx):
			return ctx.author.id == ctx.bot.config.config["headmod"]
		return commands.check(predicate)
	
	def is_staff():
		def predicate(ctx):
			staff = ctx.bot.config.config["moders"]
			staff.append(ctx.bot.config.config["owner"])
			staff.append(ctx.bot.config.config["headmod"])
			return ctx.author.id in staff
		return commands.check(predicate)
	
	async def throw_warning_window(self, ctx, verb, callback, *args, **kwargs):
		await ctx.response.send_modal(WarningWindow(self.bot, verb, callback, *args, **kwargs))

	@is_staff()
	@commands.slash_command()
	async def warns(self, ctx, user: discord.Member):
		view = WarnCard(user, ctx.author, self.bot)
		await ctx.respond(embed= view.update_embed(), view= view)


	@is_owner()
	@commands.slash_command()
	async def head(self, ctx, user: discord.Member):
		async def callback(ctx, id, config):
			config.config["headmod"] = id
			config.upload_to_file()
			await ctx.respond(f"Пользователь <@!{id}> был установлен в качестве главного модератора")

		await self.throw_warning_window(ctx, f"Назначить человека на ГлавМода", callback, ctx, user.id, self.bot.config)

	@is_owner()
	@commands.slash_command()
	async def log_channel(self, ctx, channel: discord.TextChannel):
		async def callback(ctx, id, config):
			config.config["log_channel"] = id
			config.upload_to_file()
			await ctx.repond(f"Канал <#{id}> был установлен в качестве канала для логгирования")

		await self.throw_warning_window(ctx, f"Назначить канал для логов", callback, ctx, channel.id, self.bot.config)

	@is_owner()
	@commands.slash_command()
	async def moderator(self, ctx, verb: discord.Option(name="тип", choices=[discord.OptionChoice(name="Добавить", value="1"),discord.OptionChoice(name="Убрать", value="0")], required= True), user: discord.Member):
		async def addmod(ctx, id, config):
			config.config["moders"].append(id)
			config.upload_to_file()
			await ctx.respond(f"Пользователь <@!{id}> был добавлен в список модераторов")

		async def remmod(ctx, id, config):
			try:
				config.config["moders"].remove(id)
			except:
				await ctx.respond(f"Пользователь <@!{id}> не обнаружен в списке модераторов")
				return
			config.upload_to_file()
			await ctx.respond(f"Пользователь <@!{id}> был удален из списка модераторов")

		callback = addmod if int(verb) else remmod
		await self.throw_warning_window(ctx, "Изменить список модерации", callback, ctx, user.id, self.bot.config)

def setup(bot):
	bot.add_cog(Mods(bot))
	print("Lesbian writer mods engaged!")      