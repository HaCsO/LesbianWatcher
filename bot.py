import discord
from discord.ext import commands
from utils.extern.config_holder import ConfigHolder
from utils.extern.logger import Logger

intents = discord.Intents.all()

class LesBot(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = ConfigHolder("config.toml")
		self.logger = Logger
		self.guild_id = self.config.bot["guild_id"]
		self.debug_guilds = self.config.bot["debug_guilds"]

Bot = LesBot(command_prefix="!", intents= intents)
Bot.remove_command("help")

@Bot.event
async def on_ready():
	print("[Lesbian Watcher] activated!")
	Bot.logger = Bot.logger(Bot)

@Bot.event
async def on_application_command_error(ctx, err):
	if isinstance(err, commands.errors.CommandOnCooldown):
		await ctx.respond("Команда на перезарядке...", delete_after=15)
	elif isinstance(err, discord.errors.CheckFailure):
		await ctx.respond("Не дозволено!", delete_after=15)
	elif isinstance(err, commands.errors.CommandNotFound):
		await ctx.respond("Команда не найдена", delete_after=15)
	elif isinstance(err, commands.errors.RoleNotFound):
		pass
	else:
		await ctx.respond(
			embed = discord.Embed(
				description =f"**Хуй знает какая проблема!!!**",
				color = discord.Color.red(),
			), delete_after = 15
			)
		await Bot.logger.log(f"ERROR: {err}")
		raise err	

cogs = [
	"cogs.mods",
	"cogs.votes"
]
for i in cogs:
	Bot.load_extension(i)

Bot.run(Bot.config.bot["token"])
	

