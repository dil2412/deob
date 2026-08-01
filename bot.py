import os
import sys
import subprocess
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready to deobfuscate!")

@bot.command(name="deobf")
async def deobf(ctx):
    """Usage: Upload a .txt file with the command !deobf"""
    if not ctx.message.attachments:
        await ctx.send("Please attach a text file to your message!")
        return

    attachment = ctx.message.attachments[0]
    input_path = os.path.abspath(attachment.filename)
    await attachment.save(input_path)

    try:
        # Run deobfuscator.py properly using the system executable
        result = subprocess.run(
            [sys.executable, "deobfuscator.py", input_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Determine output path (.deobf.lua)
        base_name = os.path.splitext(input_path)[0]
        output_path = base_name + ".deobf.lua"

        # Fallback check if output wasn't created with that exact name, look for generated files
        if not os.path.exists(output_path):
            report_path = base_name + ".report.txt"
            if os.path.exists(report_path):
                from trace_to_lua import parse_trace
                parse_trace(report_path)

        if os.path.exists(output_path):
            await ctx.send("Here is your deobfuscated file:", file=discord.File(output_path))
            os.remove(output_path)
        else:
            logs = result.stdout or result.stderr or "No output generated."
            await ctx.send(f"Deobfuscation finished, but no output file was found. Logs: ```{logs[:1500]}```")

    except Exception as e:
        await ctx.send(f"An error occurred during execution: ```{e}```")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: DISCORD_TOKEN environment variable not set.")
