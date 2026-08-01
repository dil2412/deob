import os
import io
import re
import string
import random
import requests
import discord
import aiohttp
import time
from discord.ext import commands
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN", "DISCORD_TOKEN")
PRETTY_MODE = True

def beautify_lua(content):
    try:
        response = requests.post(
            "https://relua.lua.cz/deobfuscate",
            json={"filename": "script.lua", "source": content, "lua_version": "Lua51", "pretty": PRETTY_MODE},
            timeout=50
        )
        response.raise_for_status()
        result = response.json()

        if "output" in result:
            return result["output"]
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

def fetch_url(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Failed to fetch URL: {e}")
        return None

def extract_link(text):
    url_match = re.search(r'(https?://[^\s]+)', text)
    return url_match.group(1) if url_match else None

def string_to_discordfile(content_str, filename="deobfuscated.lua"):
    return discord.File(fp=io.BytesIO(content_str.encode('utf-8')), filename=filename)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents, activity=discord.Game(name="Send links/files to deobf"), help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")

async def process_promdeobf(message, content_source):
    status_msg = await message.reply("Processing deobfuscation... The results will be sent to your DMs!")
    start_time = time.time()
    output = beautify_lua(content_source)

    if not output:
        await status_msg.edit(content=f"{message.author.mention} Failed to deobfuscate code via the API.")
        return

    end_time = time.time()
    processed_time = int((end_time - start_time) * 1000)
    finished_time = int((end_time - start_time) * 1000) + random.randint(1500, 3500)
    
    banner = (
        "Generated Using WeAreDevs Dumper Template"
    )
    final_output = f"--[[\n{banner}\n]]\n\n{output}"

    embed_desc = (
        f"```\n{banner}```\n"
        f"**Processed script in:** `{processed_time}ms`\n"
        f"**Finished everything in:** `{finished_time}ms`\n\n"
        "*Successfully processed code.*"
    )

    embed = discord.Embed(
        title="Here's Your Script!",
        description=embed_desc,
        color=discord.Color.from_rgb(255, 165, 0)
    )

    try:
        await status_msg.edit(content=f"{message.author.mention} Done! Check your DMs for the output.")
        await message.author.send(embed=embed)
        
        if len(final_output) <= 1900:
            await message.author.send(content=f"```lua\n{final_output}\n```")
        else:
            filename = "deobfuscated.lua"
            file_data = string_to_discordfile(final_output, filename=filename)
            await message.author.send(file=file_data)
    except Exception:
        await status_msg.edit(content=f"{message.author.mention} Done! However, I couldn't open a DM link with you. Check your privacy setup.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Restrict execution solely to the designated channel ID
    if message.channel.id != 1511627488747589674:
        return

    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(('.lua', '.txt')):
            try:
                content_bytes = await attachment.read()
                content = content_bytes.decode("utf-8", errors="ignore")
                if content.strip():
                    await process_promdeobf(message, content)
                    return
            except Exception as e:
                print(f"Failed to read attached file: {e}")

    extracted_url = extract_link(message.content)
    if extracted_url:
        content = fetch_url(extracted_url)
        if content and content.strip():
            await process_promdeobf(message, content)
            return

    await bot.process_commands(message)

bot.run(TOKEN)
