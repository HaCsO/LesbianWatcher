import discord
from discord.ext import commands
from utils.config_holder import ConfigHolder

intents = discord.Intents.all()

class LesBot(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = ConfigHolder("config.json")

Bot = LesBot(command_prefix="!", intents= intents, debug_guilds=[564902261327921186])
Bot.remove_command("help")

@Bot.event
async def on_ready():
	print("Lesbian Watcher activated!")

@Bot.event
async def on_application_command_error(ctx, err):
	if isinstance(err, commands.errors.CommandOnCooldown):
		await ctx.respond("Команда на перезарядке...", delete_after=15)
		return
	elif isinstance(err, discord.errors.CheckFailure):
		await ctx.respond("Не дозволено!", delete_after=15)
		return
	elif isinstance(err, commands.errors.CommandNotFound):
		await ctx.respond("Команда не найдена", delete_after=15)
		return
	elif isinstance(err, commands.errors.RoleNotFound):
		pass
	else:
		await ctx.respond(
			embed = discord.Embed(
				description =f"**Хуй знает какая проблема!!!**",
				color = discord.Color.red(),
			), delete_after = 15
			)
		raise err

cogs = [
	"cogs.mods",
	"cogs.votes"
]
for i in cogs:
	Bot.load_extension(i)

Bot.run("MTA3NzEyNDA2MzE0MDUxOTk4Ng.G76xDY.eUIyAjE6VHqg14ILS1y6gGWywC1QK4m311wRwg")
	

