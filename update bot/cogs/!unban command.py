import discord
from discord.ext import commands
from config import UNBAN_COMMAND_LOGS

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, user_id: int = None, *, reason: str = None):
        """Unbans a user with a reason and logs the action."""
        
        # Check if user ID and reason are provided
        if not user_id or not reason:
            await ctx.send("❌ Usage: `!unban <user_id> <reason>`", delete_after=5)
            await ctx.message.delete()
            return

        # Fetch all bans properly
        banned_users = [ban async for ban in ctx.guild.bans()]
        user = discord.utils.get(banned_users, user__id=user_id)

        if not user:
            await ctx.send("⚠️ This user is not banned or the ID is incorrect.", delete_after=5)
            await ctx.message.delete()
            return

        # Unban the user
        await ctx.guild.unban(user.user, reason=reason)
        await ctx.send(f"✅ {user.user.mention} has been unbanned.")

        # Log the unban action
        log_channel = self.bot.get_channel(UNBAN_COMMAND_LOGS)
        if log_channel:
            log_embed = discord.Embed(
                title="🔓 User Unbanned",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            log_embed.set_thumbnail(url=user.user.avatar.url if user.user.avatar else user.user.default_avatar.url)
            log_embed.add_field(name="👤 User", value=f"{user.user.mention} ({user.user.id})", inline=False)
            log_embed.add_field(name="⛔ Ban Reason", value=f"```{user.reason or 'Unknown'}```", inline=False)
            log_embed.add_field(name="📜 Unban Reason", value=f"```{reason}```", inline=False)
            log_embed.add_field(name="👑 Unbanned By", value=f"{ctx.author.mention}", inline=True)
            log_embed.add_field(name="🛠 Roles", value=", ".join([role.mention for role in ctx.author.roles if role.name != "@everyone"]) or "No Roles", inline=False)
            log_embed.set_footer(text=f"Unbanned in: {ctx.guild.name}")

            await log_channel.send(embed=log_embed)

        # Delete the original command message
        await ctx.message.delete()

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Administrator permissions to use this command.", delete_after=5)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid user ID. Please use a valid number.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Unban(bot))
