import os
import discord
from discord.ext import commands
from trace_to_lua import parse_trace

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready to deobfuscate!")

@bot.command(name="deobf")
async def deobf(ctx):
    """Usage: Upload a .report.txt file with the command !deobf"""
    if not ctx.message.attachments:
        await ctx.send("Please attach a report text file to your message!")
        return

    attachment = ctx.message.attachments[0]
    
    # Save the file locally with an absolute path
    input_path = os.path.abspath(attachment.filename)
    await attachment.save(input_path)

    try:
        # Pass the absolute path to your parsing function
        parse_trace(input_path)
        
        # Determine output filename
        output_path = input_path.replace(".report.txt", ".deobf.lua")
        if not os.path.exists(output_path):
            # Fallback if extension differs slightly
            output_path = input_path + ".deobf.lua"

        if os.path.exists(output_path):
            await ctx.send("Here is your deobfuscated file:", file=discord.File(output_path))
            
            # Clean up local files
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        else:
            await ctx.send("Deobfuscation ran, but no output file was generated.")
    except Exception as e:
        await ctx.send(f"An error occurred during deobfuscation: ```{e}```")
        if os.path.exists(input_path):
            os.remove(input_path)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: DISCORD_TOKEN environment variable not set.")
