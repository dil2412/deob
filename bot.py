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
    """Usage: Upload a .txt file with the command !deobf"""
    if not ctx.message.attachments:
        await ctx.send("Please attach a text file to your message!")
        return

    attachment = ctx.message.attachments[0]
    
    # Save the input file locally
    input_path = os.path.abspath(attachment.filename)
    await attachment.save(input_path)

    try:
        # Run your parser function
        parse_trace(input_path)
        
        # Force the output filename to end with .deobf.lua regardless of input name
        base_name = os.path.splitext(input_path)[0]
        output_path = base_name + ".deobf.lua"

        if os.path.exists(output_path):
            await ctx.send("Here is your deobfuscated file:", file=discord.File(output_path))
            
            # Clean up local files
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        else:
            await ctx.send("Deobfuscation finished, but the output file could not be located.")
    except Exception as e:
        await ctx.send(f"An error occurred during deobfuscation: ```{e}```")
        if os.path.exists(input_path):
            os.remove(input_path)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: DISCORD_TOKEN environment variable not set.")
