import datetime
import json
import discord
import tomli
import tomli_w
				
class Logger():
	def __init__(self, bot):
		self.bot = bot
		self.log_channel = None
		self.punish_channel = None
		self.guild_id = 564902261327921186
		self.update_log_channel()
		self.update_punish_channel()
		self.localisation = {
			"ru": DefaulLogMsgs("ru", "localisation/ru.toml"),
			"en": DefaulLogMsgs("en", "localisation/eng.toml")
		}
		self.choosen_localise = "ru"

	def update_log_channel(self):
		channel = self.bot.config.channels["log"]
		if not channel:
			print("Config havent a log channel id, so logs will went in console")
			return 

		try:
			self.log_channel = self.bot.get_channel(channel)
		except:
			print("Log channel not found by id in config, so, print logs into console")
			self.log_channel = None

	def update_punish_channel(self):
		channel = self.bot.config.channels["punish"]
		if not channel:
			print("Config havent a log channel id, so logs will went in console")
			return 

		try:
			self.punish_channel = self.bot.get_channel(channel)
		except:
			print("Log channel not found by id in config, so, print logs into console")
			self.punish_channel = None

	async def log(self, msg, embed= None, formats = list(), is_punish= False, lock_discord_msg= False):
		discord_msg = msg
		console_msg = msg
		if len(formats) > 1:
			for i in formats:
				discord_msg = i.discord_format(discord_msg)
				console_msg = i.console_format(console_msg)
		elif len(formats):
			discord_msg, console_msg = formats[0].do_format(msg)

		choosen_channel = self.log_channel if not is_punish else self.punish_channel

		if choosen_channel:
			await choosen_channel.send(discord_msg if not lock_discord_msg else None, embed= embed)
		else:
			print(console_msg)

		with open("logs.txt", "a", encoding="UTF8") as log_file:
			log_file.write(f"[{datetime.datetime.now()}] " + console_msg + "\n")

	async def log_localised(self, name, formats=list(), **kwargs):
		assert name in self.localisation[self.choosen_localise].locals
		message = self.localisation[self.choosen_localise].locals[name]
		emb = None
		if message["embed"] is not None:
			desc = message["embed"]["description"]
			for d in message["embed"]["dependences"]:
				desc = desc.replace(d, kwargs.get(d.lower()))
			col = 0
			col = (col << 8) + int(message["embed"]["color"][1:3], 16)
			col = (col << 8) + int(message["embed"]["color"][3:5], 16)
			col = (col << 8) + int(message["embed"]["color"][5:7], 16)
			emb = discord.Embed(title= message["embed"]["title"], description= desc, color= col)
		await self.log(message["value"], formats=formats, is_punish=message["punish"], lock_discord_msg=message["dislock"], embed= emb)
		

	class BaseFormat:
		rules: dict = {}
		def __init__(self, rules):
			self.rules = rules

		def discord_format(self, msg):
			msg_for_discord = msg
			for k, v in self.rules.items():
				msg_for_discord = msg_for_discord.replace(k, v)
			return msg_for_discord

		def console_format(self, msg):
			msg_for_console = msg
			for k, v in self.rules.items():
				msg_for_console = msg_for_console.replace(k, v)
			return msg_for_console

		def do_format(self, msg):
			return self.discord_format(msg), self.console_format(msg)

	class UserFormatType(BaseFormat):
		def discord_format(self, msg):
			msg_for_discord = msg
			for k, v in self.rules.items():
				msg_for_discord = msg_for_discord.replace(k, f"{v.mention}")
			return msg_for_discord

		def console_format(self, msg):
			msg_for_console = msg
			for k, v in self.rules.items():
				msg_for_console = msg_for_console.replace(k, f"{v.name}#{v.discriminator}")
			return msg_for_console

	class ChannelFormatType(BaseFormat):
		def discord_format(self, msg):
			msg_for_discord = msg
			for k, v in self.rules.items():
				msg_for_discord = msg_for_discord.replace(k, f"<#{v.id}>")
			return msg_for_discord

		def console_format(self, msg):
			msg_for_console = msg
			for k, v in self.rules.items():
				msg_for_console = msg_for_console.replace(k, f"{v.name}({v.id})")

			return msg_for_console

	class RoleFormatType(BaseFormat):
		def discord_format(self, msg):
			msg_for_discord = msg
			for k, v in self.rules.items():
				msg_for_discord = msg_for_discord.replace(k, f"<@&{v.id}>")
			return msg_for_discord

		def console_format(self, msg):
			msg_for_console = msg
			for k, v in self.rules.items():
				msg_for_console = msg_for_console.replace(k, f"{v.name}({v.id})")
			return msg_for_console

	class DiscordFormatType(BaseFormat):
		def __init__(self):
			self.rules = {
				"ITALIC": "*",
				"BOLD": "**",
				"REPLY": "```"
			}

		def discord_format(self, msg):
			msg_for_discord = msg
			for k, v in self.rules.items():
				msg_for_discord = msg_for_discord.replace(k, v)
			return msg_for_discord

		def console_format(self, msg):
			msg_for_console = msg
			for k, v in self.rules.items():
				msg_for_console = msg_for_console.replace(k, "")
			return msg_for_console

class DefaulLogMsgs():
	def __init__(self, localisation, file):
		self.locname = localisation
		self.file = file
		self.locals = {}
		self.__parse()

	def __parse(self):
		with open(self.file, "rb") as f:
			data = tomli.load(f)
			info = data["main"]
			embeds = data["embeds"]
			for name, value in info.items():
				self.locals[name] = {"value": value[0], "punish": int(value[1]), "dislock": int(value[2]), "embed": None}
			for name, value in embeds.items():
				if name in self.locals:
					self.locals[name]["embed"] = json.loads(value, strict= False)
			