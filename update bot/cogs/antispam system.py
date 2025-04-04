import discord
from discord.ext import commands
import time
from collections import defaultdict
from config import ANTI_SPAM_LOGS  # Import log channel ID

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_log = defaultdict(list)  # Stores user messages
        self.warn_cooldown = {}  # Prevents repeated warnings per user

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return  # Ignore bot messages & DMs

        guild = message.guild
        user = message.author
        user_id = user.id
        content = message.content
        channel = message.channel
        timestamp = time.time()

        # Log user's messages (keep recent)
        self.message_log[user_id].append((content, timestamp, channel.id))

        # Remove old messages (only keep last 4 seconds)
        self.message_log[user_id] = [(msg, ts, ch) for msg, ts, ch in self.message_log[user_id] if timestamp - ts <= 4]

        # **Spam Detection**
        same_message_spam = sum(1 for msg, ts, ch in self.message_log[user_id] if msg == content) >= 5
        general_spam = len(self.message_log[user_id]) >= 5 and (timestamp - self.message_log[user_id][0][1]) <= 3

        if same_message_spam or general_spam:
            # **Cooldown (Prevent spam warnings every 15 sec)**
            if user_id in self.warn_cooldown and time.time() - self.warn_cooldown[user_id] < 15:
                return  

            self.warn_cooldown[user_id] = time.time()  # Set cooldown

            # ✅ **Reply to the spammer's last message**
            await message.reply("✅ **Stop spamming!**", mention_author=True)

            # **📜 LOG EMBED**
            log_channel = self.bot.get_channel(ANTI_SPAM_LOGS)  # Get log channel from config
            if log_channel:
                log_embed = discord.Embed(
                    title="🛑 **Anti-Spam Alert**",
                    color=discord.Color.orange(),
                    timestamp=discord.utils.utcnow()
                )
                log_embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
                log_embed.add_field(name="👤 **User**", value=f"**{user.name}** (`{user.id}`)", inline=True)
                log_embed.add_field(name="📍 **Channel**", value=f"<#{channel.id}>", inline=True)  # Clickable Channel
                log_embed.add_field(name="🕒 **Time**", value=f"<t:{int(timestamp)}:R>", inline=True)
                log_embed.add_field(name="📜 **Spam Messages**", value="\n".join(f"```{msg}```" for msg, ts, ch in self.message_log[user_id][-5:]), inline=False)
                log_embed.add_field(name="📌 **Log Channel**", value=f"<#{ANTI_SPAM_LOGS}>", inline=False)  # Clickable Log Channel

                log_embed.set_footer(text=f"Server: {guild.name}", icon_url=guild.icon.url if guild.icon else None)

                try:
                    await log_channel.send(embed=log_embed)
                except discord.Forbidden:
                    print(f"Error: Bot lacks permission to send messages in {ANTI_SPAM_LOGS}")
                except Exception as e:
                    print(f"Unexpected error sending logs: {e}")

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
