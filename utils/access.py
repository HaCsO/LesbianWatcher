from discord.ext import commands

def is_talk_channel():
    def predicate(ctx):
        channel = ctx.bot.config.config["talk_channel"]
        if not channel:
            return True
        return ctx.channel.id == channel
    return commands.check(predicate)

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