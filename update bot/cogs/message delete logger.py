import discord
from discord.ext import commands
from discord import Embed
from discord.ext.commands import Context
import logging

# Assuming you have the logging channel ID in your config.py
from config import MESSAGE_DELETE_LOGS  # Update with the correct import from your config

class MessageDeleteLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Exclude bot messages
        if message.author.bot:
            return

        # Get the log channel from the config file
        log_channel = self.bot.get_channel(MESSAGE_DELETE_LOGS)

        if log_channel is None:
            print("Log channel not found. Please check the MESSAGE_DELETE_LOGS ID in config.py")
            return

        # Get the message author and their roles
        author = message.author
        author_roles = [role.mention for role in author.roles if role.name != "@everyone"]
        author_roles_str = ", ".join(author_roles) if author_roles else "No roles"

        # Create the embed for the deleted message log
        embed = Embed(
            title=f"🚮 Message Deleted",
            description=f"**📝 Message Content:**\n```{message.content or 'No content'}\n```",  # Message content in a black box
            color=discord.Color.red(),
            timestamp=message.created_at  # Timestamp of when the message was deleted
        )

        # Add fields with emojis
        embed.add_field(name="👤 Author", value=author.mention, inline=False)
        embed.add_field(name="🔑 Author Roles", value=author_roles_str, inline=False)
        embed.add_field(name="📚 Channel", value=message.channel.mention, inline=False)

        # Add a footer with the user's ID and the deletion timestamp
        embed.set_footer(text=f"🔍 User ID: {author.id} | Deleted at:")
        embed.set_thumbnail(url=author.avatar.url)  # Display the author's avatar

        # Send the embed to the log channel
        await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MessageDeleteLogger(bot))
