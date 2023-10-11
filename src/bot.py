import discord
from dotenv import load_dotenv
import os
from db import DB
import threading
from twitter import process_twitter_space
import asyncio

bot = discord.Bot()
load_dotenv()

db = DB()


@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name)


@bot.slash_command()
async def list(ctx):
    current_watchlist = db.get_watchlist()
    await ctx.respond("Current watchlist: " + ", ".join(current_watchlist))


@bot.slash_command()
async def add(ctx, twitter_url: str):
    db.add_to_watchlist(twitter_url)
    await ctx.respond("Added user to watchlist")


@bot.slash_command()
async def remove(ctx, twitter_url: str):
    db.remove_from_watchlist(twitter_url)
    await ctx.respond("Removed user from watchlist")


async def run_in_executor(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


async def notify_user(ctx, space_url):
    try:
        res = await run_in_executor(process_twitter_space, space_url, "cookies.txt")
        with open("summary.txt", "w") as file:
            file.write(res["notes"])

        await ctx.send(res["exec_sum"])
        await ctx.send(file=discord.File("summary.txt"))
    except Exception as e:
        await ctx.send(f"Error processing {space_url}: {e}")


@bot.slash_command()
async def process(ctx, space_url: str):
    await ctx.respond(f"Processing space URL {space_url}... I'll notify you when it's done.")

    # This will run process_twitter_space in a thread
    asyncio.create_task(notify_user(ctx, space_url))

bot.run(os.getenv("DISCORD_TOKEN"))
