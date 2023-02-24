import discord
from discord.ext import commands, tasks
import sqlite3
import json
import datetime
from .gui_assets import *

class Mods(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		self.un.start()

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
	
	def is_headstaff():
		def predicate(ctx):
			staff = [ctx.bot.config.config["headmod"], ctx.bot.config.config["owner"]]
			return ctx.author.id in staff
		return commands.check(predicate)
	
	async def throw_warning_window(self, ctx, verb, callback, *args, **kwargs):
		await ctx.response.send_modal(WarningWindow(self.bot, verb, callback, *args, **kwargs))

	async def regive_role(self, member, role):
		formats = [self.bot.logger.UserFormatType({"USER": member})]
		await self.bot.logger.log("Пользователь USER попытался перезайти на сервер имея активное наказание!", formats= formats)
		if not role:
			await self.bot.logger.log(f"{self.author.mention} Внимание, не обнаружена роль. Проверьте конфигурацию!")
			return
		
		try:
			role = self.bot.get_guild(self.bot.guild_id).get_role(role)
		except:
			await self.bot.logger.log(f"{self.author.mention} Внимание, не обнаружена роль. Проверьте конфигурацию!")
			return None
		
		await member.add_roles(role)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		res, db, cur = get_structured_db_info(self.user)
		db.close()

		if not res:
			return
		
		if json.loads(res[3]):
			role = self.bot.config.config["mime_role"]
			await self.regive_role(member, role)

		if json.loads(res[4]):
			role = self.bot.config.config["clown_role"]
			await self.regive_role(member, role)

	@is_headstaff()
	@commands.slash_command()
	async def force_mime(self, ctx, user: discord.Member, reason= "Не указана"):
		warn = Punish(ctx.author, user, self.bot)
		await warn.mime(reason)
		await ctx.respond("Выполнено!")

	@is_headstaff()
	@commands.slash_command()
	async def force_clown(self, ctx, user: discord.Member, reason= "Не указана"):
		warn = Punish(ctx.author, user, self.bot)
		await warn.clown(reason)
		await ctx.respond("Выполнено!")

	@is_headstaff()
	@commands.slash_command()
	async def unmime(self, ctx, user: discord.Member):
		warn = Punish(ctx.author, user, self.bot)
		await warn.unmime()
		await ctx.respond("Выполнено!")

	@is_headstaff()
	@commands.slash_command()
	async def unclown(self, ctx, user: discord.Member):
		warn = Punish(ctx.author, user, self.bot)
		await warn.unclown()
		await ctx.respond("Выполнено!")

	@is_staff()
	@commands.slash_command()
	async def warns(self, ctx, user: discord.Option(discord.Member, "Укажите пользователя", required = False)):
		if user:
			view = WarnCard(user, ctx.author, self.bot)
			await ctx.respond(embed= view.update_embed(), view= view)
			return
		
		db = sqlite3.connect("data.db")
		cur = db.cursor()
		cur.execute("SELECT * FROM warn")
		desc = ""
		res = cur.fetchall()
		for us in res:
			duser = self.bot.get_guild(self.bot.guild_id).get_member(int(us[0]))
			desc += f"{duser.mention} - {us[2]} варнов{' - КЛОУН' if len(json.loads(us[4])) else ''} {' - МИМ' if len(json.loads(us[3])) else ''}"

		emb = discord.Embed(title="Список нарушителей", description=desc, color=0xffa586)
		await ctx.respond(embed= emb)
	@is_staff()
	@commands.slash_command()
	async def warn(self, ctx, user: discord.Member, reason= "Не указано"):
		warn = Punish(ctx.author, user, self.bot)
		await warn.warn(reason)
		await ctx.respond("Выполнено!")

	@is_staff()
	@discord.message_command(name= "Выдать варн")
	async def warn_msg(self, ctx, msg):
		modal = WarnGive(self.bot, ctx.author, msg.author, msg)
		await ctx.send_modal(modal)

	@is_owner()
	@commands.slash_command()
	async def head(self, ctx, user: discord.Member):
		async def callback(ctx, id, config, bot):
			config.config["headmod"] = id
			config.upload_to_file()
			await ctx.respond(f"Пользователь <@!{id}> был установлен в качестве главного модератора")
			formats = [bot.logger.UserFormatType({"AUTHOR": ctx.author, "USER": user})]
			await bot.logger.log(msg= f"Пользователь AUTHOR выдал пользователю USER должность главного модератора", formats= formats)

		await self.throw_warning_window(ctx, f"Назначить человека на ГлавМода", callback, ctx, user.id, self.bot.config, self.bot)

	@is_owner()
	@commands.slash_command()
	async def log_channel(self, ctx, channel: discord.TextChannel):
		async def callback(ctx, id, config, bot):
			config.config["log_channel"] = id
			config.upload_to_file()
			await ctx.respond(f"Канал <#{id}> был установлен в качестве канала для логгирования")
			bot.logger.update_log_channel()
			formats = [bot.logger.UserFormatType({"AUTHOR": ctx.author}), bot.logger.ChannelFormatType({"CHANNEL": channel})]
			await bot.logger.log(msg= f"Пользователь AUTHOR установил канал CHANNEL в качестве канала для логгирования", formats= formats)

		await self.throw_warning_window(ctx, f"Назначить канал для логов", callback, ctx, channel.id, self.bot.config, self.bot)

	@is_owner()
	@commands.slash_command()
	async def mime_role(self, ctx, role: discord.Role):
		async def callback(ctx, id, config, bot):
			config.config["mime_role"] = id
			config.upload_to_file()
			await ctx.respond(f"Роль <@&{id}> была установлен в качестве роли мима")
			formats = [bot.logger.UserFormatType({"AUTHOR": ctx.author}), bot.logger.RoleFormatType({"ROLE": role})]
			await bot.logger.log(msg= f"Пользователь AUTHOR установил роль ROLE в качестве роли мима", formats= formats)

		await self.throw_warning_window(ctx, f"Назначить канал для логов", callback, ctx, role.id, self.bot.config, self.bot)

	@is_owner()
	@commands.slash_command()
	async def clown_role(self, ctx, role: discord.Role):
		async def callback(ctx, id, config, bot):
			config.config["clown_role"] = id
			config.upload_to_file()
			await ctx.respond(f"Роль <@&{id}> была установлен в качестве роли клоуна")
			formats = [bot.logger.UserFormatType({"AUTHOR": ctx.author}), bot.logger.RoleFormatType({"ROLE": role})]
			await bot.logger.log(msg= f"Пользователь AUTHOR установил роль ROLE в качестве роли клоуна", formats= formats)

		await self.throw_warning_window(ctx, f"Назначить канал для логов", callback, ctx, role.id, self.bot.config, self.bot)


	@is_owner()
	@commands.slash_command()
	async def punish_channel(self, ctx, channel: discord.TextChannel):
		async def callback(ctx, id, config, bot):
			config.config["punish_channel"] = id
			config.upload_to_file()
			await ctx.respond(f"Канал <#{id}> был установлен в качестве канала для логгирования наказаний")
			bot.logger.update_punish_channel()
			formats = [bot.logger.UserFormatType({"AUTHOR": ctx.author}), bot.logger.ChannelFormatType({"CHANNEL": channel})]
			await bot.logger.log(msg= f"Пользователь AUTHOR установил канал CHANNEL в качестве канала для логгирования наказаний", formats= formats)

		await self.throw_warning_window(ctx, f"Назначить канал для наказа", callback, ctx, channel.id, self.bot.config, self.bot)


	@is_owner()
	@commands.slash_command()
	async def moderator(self, ctx, verb: discord.Option(name="тип", choices=[discord.OptionChoice(name="Добавить", value="1"),discord.OptionChoice(name="Убрать", value="0")], required= True), user: discord.Member):
		async def addmod(ctx, id, config, bot):
			if id in config.config["moders"]:
				await ctx.respond(f"Пользователь <@!{id}> уже в список модераторов")
				return
			
			config.config["moders"].append(id)
			config.upload_to_file()
			await ctx.respond(f"Пользователь <@!{id}> был добавлен в список модераторов")
			formats = [bot.logger.UserFormatType({"AUTHOR": ctx.author, "USER": user})]
			await bot.logger.log(msg= f"Пользователь AUTHOR добавил пользователя USER в список модерации", formats= formats)

		async def remmod(ctx, id, config, bot):
			try:
				config.config["moders"].remove(id)
			except:
				await ctx.respond(f"Пользователь <@!{id}> не обнаружен в списке модераторов")
				return
			config.upload_to_file()
			await ctx.respond(f"Пользователь <@!{id}> был удален из списка модераторов")
			formats = [bot.logger.UserFormatType({"AUTHOR": ctx.author, "USER": user})]
			await bot.logger.log(msg= f"Пользователь AUTHOR удалил пользователя USER из списока модерации", formats= formats)

		callback = addmod if int(verb) else remmod
		await self.throw_warning_window(ctx, "Изменить список модерации", callback, ctx, user.id, self.bot.config, self.bot)

	@is_headstaff()
	@commands.slash_command()
	async def get_logs(self, ctx):
		await ctx.respond(file= discord.File("logs.txt"))

	@tasks.loop(minutes=5)
	async def un(self):
		db = sqlite3.connect("data.db")
		cur = db.cursor()
		cur.execute("SELECT * FROM warn")
		dat = cur.fetchall()
		checktime = datetime.datetime.now()
		for user in dat:
			warns = json.loads(user[1])
			mime = json.loads(user[3])
			clown = json.loads(user[4])
			if len(mime):
				if datetime.datetime.fromtimestamp(float(mime["datetime"])) + datetime.timedelta(days=7) < checktime:
					duser = self.bot.get_guild(self.bot.guild_id).get_member(int(user[0]))
					warncontent = Punish(self.bot.user, duser, self.bot)
					await warncontent.unmime()
				continue

			elif len(clown):
				if datetime.datetime.fromtimestamp(float(clown["datetime"])) + datetime.timedelta(days=7) < checktime:
					duser = self.bot.get_guild(self.bot.guild_id).get_member(int(user[0]))
					warncontent = Punish(self.bot.user, duser, self.bot)
					await warncontent.unclown()
				continue

			if len(warns):
				for warn_place, warn in warns.items():
					if datetime.datetime.fromtimestamp(float(warn["datetime"])) + datetime.timedelta(days=7) < checktime:
						duser = self.bot.get_guild(self.bot.guild_id).get_member(int(user[0]))
						warncontent = Punish(self.bot.user, duser, self.bot)
						await warncontent.unwarn(warn_place)

def setup(bot):
	bot.add_cog(Mods(bot))
	print("Lesbian Wathcer mods engaged!")      