import datetime

class Logger():
	def __init__(self, bot):
		self.bot = bot
		self.log_channel = None
		self.punish_channel = None
		self.guild_id = 564902261327921186
		self.update_log_channel()
		self.update_punish_channel()

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
		else:
			discord_msg, console_msg = formats[0].do_format(discord_msg)

		choosen_channel = self.log_channel if not is_punish else self.punish_channel

		if choosen_channel:
			await choosen_channel.send(discord_msg if not lock_discord_msg else None, embed= embed)
		else:
			print(console_msg)

		with open("logs.txt", "a", encoding="UTF8") as log_file:
			log_file.write(f"[{datetime.datetime.now()}] " + console_msg + "\n")

	class BaseFormat:
		def discord_format(self, msg):
			return msg

		def console_format(self, msg):
			return msg

		def do_format(msg):
			return msg, msg

	class UserFormatType(BaseFormat):
		# {"messagetoreplace": discord.Member}
		def __init__(self, rules):
			self.rules = rules

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

		def do_format(self, msg):
			msg_for_console = msg
			msg_for_discord = msg
			for k, v in self.rules.items():
				msg_for_console = msg_for_console.replace(k, f"{v.name}#{v.discriminator}")
				msg_for_discord = msg_for_discord.replace(k, f"{v.mention}")

			return msg_for_discord, msg_for_console

	class ChannelFormatType(BaseFormat):
		def __init__(self, rules):
			self.rules = rules

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

		def do_format(self, msg):
			msg_for_console = msg
			msg_for_discord = msg
			for k, v in self.rules.items():
				msg_for_console = msg_for_console.replace(k, f"{v.name}({v.id})")
				msg_for_discord = msg_for_discord.replace(k, f"<#{v.id}>")

			return msg_for_discord, msg_for_console

	class RoleFormatType(BaseFormat):
		def __init__(self, rules):
			self.rules = rules

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

		def do_format(self, msg):
			msg_for_console = msg
			msg_for_discord = msg
			for k, v in self.rules.items():
				msg_for_console = msg_for_console.replace(k, f"{v.name}({v.id})")
				msg_for_discord = msg_for_discord.replace(k, f"<@&{v.id}>")

			return msg_for_discord, msg_for_console

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

		def do_format(self, msg):
			msg_for_console = msg
			msg_for_discord = msg
			for k, v in self.rules.items():
				msg_for_console = msg_for_console.replace(k, "")
				msg_for_discord = msg_for_discord.replace(k, v)

			return msg_for_discord, msg_for_console
					
