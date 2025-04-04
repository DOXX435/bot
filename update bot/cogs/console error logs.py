import discord
from discord.ext import commands
from config import CONSOLE_ERROR_LOGS  # Log channel from config

class ErrorLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handles errors and logs them to the error log channel in a clean format."""
        error_channel = self.bot.get_channel(CONSOLE_ERROR_LOGS)

        if not error_channel:
            return  # If the channel isn't found, don't log

        # Get the error message only (without traceback)
        error_message = str(error).split("\n")[-1]  # Only show the last line of the error

        # Create the embed
        error_embed = discord.Embed(title="⚠️ **Bot Error Detected**", color=discord.Color.red())
        error_embed.add_field(name="📍 **Command Used**", value=f"`{ctx.message.content}`", inline=False)
        error_embed.add_field(name="👤 **User**", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=True)
        error_embed.add_field(name="🌍 **Server**", value=f"{ctx.guild.name} (`{ctx.guild.id}`)", inline=True)
        error_embed.add_field(name="📜 **Channel**", value=f"{ctx.channel.mention}", inline=True)
        error_embed.add_field(name="💥 **Error**", value=f"```{error_message}```", inline=False)

        error_embed.set_footer(text="Check the bot logs if more details are needed.")

        # Send the error embed to the log channel
        await error_channel.send(embed=error_embed)

async def setup(bot):
    await bot.add_cog(ErrorLogger(bot))
