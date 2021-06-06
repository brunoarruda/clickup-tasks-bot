#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from discord.ext import commands

client = commands.Bot(command_prefix = '$')

@client.event
async def on_ready():
    print("bot online")

@client.command()
async def ping(message):
    await message.send("pong!")


client.run(os.getenv("DISCORD_TOKEN")) #get your bot token and make a file called ".env" then inside the file write TOKEN=put your api key here example in env.txt
