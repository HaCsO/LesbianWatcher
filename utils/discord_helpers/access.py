from discord.ext import commands

def is_talk_channel():
    def predicate(ctx):
        channel = ctx.bot.config.channels["talk"]
        if not channel:
            return True
        return ctx.channel.id == channel
    return commands.check(predicate)

def is_moderator():
    def predicate(ctx):
        mods = ctx.bot.config.users["mods"]
        return ctx.author.id in mods
    return commands.check(predicate)

def is_owner():
    def predicate(ctx):
        return ctx.author.id == ctx.bot.config.users["owner"]
    return commands.check(predicate)

def is_headmod():
    def predicate(ctx):
        return ctx.author.id == ctx.bot.config.users["headmod"]
    return commands.check(predicate)

def is_staff():
    def predicate(ctx):
        staff = ctx.bot.config.users["mods"]
        staff.append(ctx.bot.config.users["owner"])
        staff.append(ctx.bot.config.users["headmod"])
        return ctx.author.id in staff
    return commands.check(predicate)

def is_headstaff():
    def predicate(ctx):
        staff = [ctx.bot.config.users["headmod"], ctx.bot.config.users["owner"]]
        return ctx.author.id in staff
    return commands.check(predicate)