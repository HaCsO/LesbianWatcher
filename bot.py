import discord
from discord.ext import commands
from utils.extern.config_holder import ConfigHolder
from utils.extern.logger import Logger
from utils.database import DBHolder

intents = discord.Intents.all()

class LesBot(commands.Bot):
	loginit = False
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		super().remove_command("help")

		self.logger = Logger
		self.dbholder = DBHolder("data.db")

		self.config = ConfigHolder("config.toml")
		self.debug_guilds = self.config.bot["debug_guilds"]
		self.guild_id = self.config.bot["guild_id"]

	async def warn_headmod_about_clown(self, user):
		if self.config.channels["talk"]: # i just CANT move this in config, because im lazy. And yeah, localisation go nahuy
			emb = discord.Embed(title="Клоун", description=f"Пользователь {user.mention} получил статус клоуна. Рекомендуется полная его блокировка!", color=0xff0000)
			await self.get_channel(self.config.channels["talk"]).send(f"<@!{self.config.users['headmod']}>", embed= emb)

	async def get_user_by_known_guild(self, id):
		return self.get_guild(self.guild_id).get_member(id)

	async def get_role_by_known_guild(self, id):
		return self.get_guild(self.get_guild).get_role(id)
	
	async def get_channel_by_known_guild(self, id):
		return self.get_guild(self.guild_id).get_channel(id)

Bot = LesBot(command_prefix="!", intents= intents)

@Bot.event
async def on_ready():
	print("[Lesbian Watcher] activated!")
	if not Bot.loginit:
		Bot.logger = Bot.logger(Bot)
		Bot.loginit = True

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
		await Bot.logger.log(f"ERROR: {err}")
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

Bot.run(Bot.config.bot["token"])
	

