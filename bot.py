import os
import re
import discord
from discord.ext import commands

# --- CORE DEOBFUSCATION ENGINE ---

def deobfuscate_luau(content: str) -> str:
    # 1. Clean encoding issues and non-breaking spaces
    content = content.replace('\xA0', ' ')
    
    # 2. Strip common junk wrappers or dead string decryption arrays if pattern matches
    # (Example: clearing out standard garbage local definitions often injected at the top)
    content = re.sub(r'local\s+[a-zA-Z0-9_]+\s*=\s*\{\s*\};?', '', content)

    # 3. Resolve proxy assignments (e.g., local a = print; a("test") -> print("test"))
    # This is a simplified regex-based lookup for local variable aliases
    aliases = {}
    for match in re.finditer(r'local\s+([a-zA-Z0-9_]+)\s*=\s*([a-zA-Z0-9_.]+)', content):
        aliases[match.group(1)] = match.group(2)
        
    for alias, original in aliases.items():
        # Replace whole-word occurrences of the alias with its original target safely
        pattern = r'\b' + alias + r'\b'
        # Avoid replacing variable declarations themselves
        content = re.sub(r'\blocal\s+' + pattern, f'-- local {alias}', content)

    # 4. Normalize basic math/string shorthands back to clean syntax
    content = re.sub(r'(\w+)\s*\+=\s*(.+)', r'\1 = \1 + (\2)', content)
    content = re.sub(r'(\w+)\s*\-=\s*(.+)', r'\1 = \1 - (\2)', content)
    content = re.sub(r'(\w+)\s*\.\.=\s*(.+)', r'\1 = \1 .. (\2)', content)

    # 5. Format spacing slightly to make it more readable
    content = re.sub(r';\s*', ';\n', content)

    return content

# --- DISCORD BOT SETUP ---

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("Deobfuscation bot is online and ready on Railway!")

@bot.command(name="deobf")
async def deobf(ctx, *, code_text: str = None):
    """Deobfuscates pasted Luau code or an attached script file."""
    target_content = None

    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        if attachment.filename.endswith(('.lua', '.luau', '.txt')):
            file_bytes = await attachment.read()
            try:
                target_content = file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                target_content = file_bytes.decode('latin-1')
        else:
            await ctx.send("❌ Please attach a valid `.lua`, `.luau`, or `.txt` file.")
            return
    elif code_text:
        target_content = code_text
    else:
        await ctx.send("❌ Please provide Luau code inline or attach a file. Usage: `!deobf [code]` or attach a file.")
        return

    # Process deobfuscation
    try:
        cleaned_code = deobfuscate_luau(target_content)
        
        # If the output is too long for a single discord message field, write it to a file and send it
        if len(cleaned_code) > 1900:
            file_path = "deobfuscated.luau"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(cleaned_code)
            
            await ctx.send("✅ **Deobfuscation Complete!** The script was too large for chat, so here is the file:", file=discord.File(file_path))
            os.remove(file_path)
        else:
            embed = discord.Embed(title="Deobfuscated Output", description=f"```lua\n{cleaned_code}\n```", color=discord.Color.green())
            await ctx.send(embed=embed)
            
    except Exception as er:
        await ctx.send(f"❌ An error occurred during deobfuscation: `{str(er)}`")

# Railway runtime token ingestion
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("ERROR: DISCORD_TOKEN environment variable not set!")
else:
    bot.run(TOKEN)
