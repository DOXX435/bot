import discord
import os
import logging
import datetime
from discord.ext import commands
from config import TOKEN, PREFIX, BOT_STARTUP_LOGS  # Ensure BOT_STARTUP_LOGS is in your config

# Set up logging
logging.basicConfig(level=logging.INFO)

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Function to load cogs
async def load_cogs():
    total_cogs = 0
    loaded_cogs = []
    failed_cogs = []

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            total_cogs += 1
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                loaded_cogs.append(cog_name)
                logging.info(f"✅ Loaded {filename}")
            except Exception as e:
                failed_cogs.append((cog_name, str(e)))
                logging.error(f"❌ Failed to load {filename}: {e}")

    return total_cogs, loaded_cogs, failed_cogs

# Event when the bot is ready
@bot.event
async def on_ready():
    logging.info(f"✅ Logged in as {bot.user} ({bot.user.id})")

    # Load cogs and get status
    total_cogs, loaded_cogs, failed_cogs = await load_cogs()

    # Get the startup log channel
    startup_channel = bot.get_channel(BOT_STARTUP_LOGS)
    if not startup_channel:
        logging.error("❌ Startup log channel not found. Check BOT_STARTUP_LOGS in config.py")
        return

    # Bot details
    bot_name = bot.user.name
    bot_id = bot.user.id
    bot_avatar = bot.user.avatar.url if bot.user.avatar else discord.Embed.Empty
    start_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Format cog lists
    loaded_cogs_text = "\n".join([f"✅ `{cog}`" for cog in loaded_cogs]) if loaded_cogs else "None"
    failed_cogs_text = "\n".join([f"❌ `{cog}` - `{error}`" for cog, error in failed_cogs]) if failed_cogs else "None"

    # Create embed
    embed = discord.Embed(
        title="🚀 **Bot Started Successfully!**",
        description="🔄 **All systems are online!**",
        color=discord.Color.green(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_thumbnail(url=bot_avatar)
    embed.add_field(name="🤖 **Bot**", value=f"👤 **Name:** `{bot_name}`\n🆔 **ID:** `{bot_id}`", inline=False)
    embed.add_field(name="🕒 **Start Time**", value=f"`{start_time}`", inline=False)
    embed.add_field(name="⚙️ **Loaded Cogs**", value=loaded_cogs_text, inline=False)
    embed.add_field(name="🚨 **Failed Cogs**", value=failed_cogs_text, inline=False)
    embed.set_footer(text=f"📦 Loaded {len(loaded_cogs)}/{total_cogs} cogs | ✅ Bot is running!")

    # Send embed to startup log channel
    await startup_channel.send(embed=embed)

    
# Run the bot
bot.run(TOKEN)
