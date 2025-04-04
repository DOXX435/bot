import discord
from discord.ext import commands
import asyncio
from discord import Embed
from datetime import datetime

# Ensure you import your configuration (where MASS_MESSAGE_DELETE_LOGS is defined)
from config  import MASS_MESSAGE_DELETE_LOGS  # Update path

class PurgeDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx):
        """
        Purge all messages in the current channel.
        """
        channel = ctx.channel
        guild = ctx.guild
        user = ctx.author

        try:
            # Fetch all messages (no flatten, using list comprehension instead)
            messages = [msg async for msg in channel.history(limit=10000)]  # Adjust the limit as needed

            # Delete all messages
            deleted_messages = len(messages)
            await channel.purge(limit=10000)

            # User roles formatted with mentions
            roles_mention = " ".join([role.mention for role in user.roles if role.name != "@everyone"])

            # Embed Message after Purge
            embed = Embed(
                title="🧹 Channel Purged!",
                description=f"All messages have been deleted in {channel.mention}.\n\n**Action performed by:** {user.mention}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_image(url="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExanlwdWlzOXN2OHlqandiNnZwMW45MG13ZWM5bWh2bm8zdDhrYjhueCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/HhTXt43pk1I1W/giphy.gif")
            embed.set_footer(text="Purge successful ✅")

            # Send the embed in the same channel
            await ctx.send(embed=embed)

            # Log the action
            log_channel = self.bot.get_channel(MASS_MESSAGE_DELETE_LOGS)
            log_embed = Embed(
                title="🚨 Mass Purge Log",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            log_embed.add_field(name="🔨 Command Used By", value=f"{user.mention} ({user.id})", inline=False)
            log_embed.add_field(name="🧹 Messages Deleted", value=f"Deleted **{deleted_messages}** messages in total.", inline=False)
            log_embed.add_field(name="📍 Channel", value=f"{channel.mention}", inline=False)
            log_embed.add_field(name="🌍 Server", value=f"{guild.name}", inline=False)
            log_embed.add_field(name="🕒 Time", value=f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", inline=False)
            log_embed.add_field(name="⚙️ Command", value="`!purge`", inline=False)
            log_embed.add_field(name="👥 User Roles", value=f"{roles_mention}", inline=False)

            if log_channel:
                await log_channel.send(embed=log_embed)

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, number: int = None):
        """
        Delete a specific number of messages.
        """
        if number is None or number < 1:
            await ctx.send("⚠️ **Please specify a valid number of messages to delete!**\nExample: `!delete 10`")
            return

        channel = ctx.channel
        guild = ctx.guild
        user = ctx.author

        try:
            # Fetch messages properly (no flatten)
            messages = [msg async for msg in channel.history(limit=number)]

            # Delete the messages
            deleted_messages = len(messages)
            await channel.purge(limit=number)

            # User roles formatted with mentions
            roles_mention = " ".join([role.mention for role in user.roles if role.name != "@everyone"])

            # Embed Message after Delete
            embed = Embed(
                title="🗑️ Messages Deleted!",
                description=f"Deleted **{deleted_messages}** messages from {channel.mention}.\n\n**Action performed by:** {user.mention}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_image(url="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExanlwdWlzOXN2OHlqandiNnZwMW45MG13ZWM5bWh2bm8zdDhrYjhueCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/HhTXt43pk1I1W/giphy.gif")
            embed.set_footer(text="Message deletion successful ✅")

            # Send the embed in the same channel
            await ctx.send(embed=embed)

            # Log the action
            log_channel = self.bot.get_channel(MASS_MESSAGE_DELETE_LOGS)
            log_embed = Embed(
                title="🚨 Mass Message Delete Log",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            log_embed.add_field(name="🔨 Command Used By", value=f"{user.mention} ({user.id})", inline=False)
            log_embed.add_field(name="🧹 Messages Requested", value=f"User requested to delete **{number}** messages.", inline=False)
            log_embed.add_field(name="🧹 Messages Deleted", value=f"Deleted **{deleted_messages}** messages in total.", inline=False)
            log_embed.add_field(name="📍 Channel", value=f"{channel.mention}", inline=False)
            log_embed.add_field(name="🌍 Server", value=f"{guild.name}", inline=False)
            log_embed.add_field(name="🕒 Time", value=f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", inline=False)
            log_embed.add_field(name="⚙️ Command", value=f"`!delete {number}`", inline=False)
            log_embed.add_field(name="👥 User Roles", value=f"{roles_mention}", inline=False)

            if log_channel:
                await log_channel.send(embed=log_embed)

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @purge.error
    @delete.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("🚫 **You do not have permission to use this command.**")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ **Please provide a valid argument!**\nExample: `!delete 10`")
        else:
            await ctx.send(f"⚠️ **An unexpected error occurred:** {error}")


# Async setup function to load the cog
async def setup(bot):
    await bot.add_cog(PurgeDelete(bot))
