#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Discord Bot doc: https://discordpy.readthedocs.io/en/stable/api.html

import asyncio
import os
import clickup
import traceback
from discord.ext import commands

client = commands.Bot(command_prefix = '$')

@client.event
async def on_ready():
    print("bot online")

@client.command()
async def task(ctx: commands.context.Context, *, args):
    try:
        meta, name, description, fields = [x for x in args.split('\n') if x != '']
        if meta.count('.') == 1:
            meta = meta.replace('.', '..')
        space, folder, list = meta.split('.')
        task = clickup.Task(space, folder, list, name, description, fields)
        client = clickup.Client(os.getenv('CLICKUP_TOKEN'))
        task = await client.create_task(task)
        msg = 'Task #{0[id]} created by {0[creator][username]}. Link: https://app.clickup.com/t/{0[id]}'.format(task)
    except Exception as e:
        msg = 'Error: {}'.format(traceback.print_exception(e))
    await ctx.send(msg)

@client.command()
async def token(ctx: commands.context.Context, app, value):
    await ctx.send("{}={}".format(app, value))

@client.event
async def on_reaction(reaction, user):
    pass

def main():
    client.run(os.getenv("DISCORD_TOKEN")) #get your bot token and make a file called ".env" then inside the file write TOKEN=put your api key here example in env.txt

if __name__ == '__main__':
    main()
