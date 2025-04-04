import discord
from discord.ext import commands
from config import DM_USER_BOT_LOGS

class DMUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def dmuser(self, ctx, member: discord.Member = None, *, message: str = None):
        """DMs a user with a message and logs it."""
        
        # Check if member and message are provided
        if not member or not message:
            error_msg = await ctx.send("❌ Usage: `!dmuser @user message`", delete_after=3)
            await ctx.message.delete()
            return
        
        # Delete the original command message
        await ctx.message.delete()
        
        # Create an embed for the DM
        dm_embed = discord.Embed(
            title="📩 New Message",
            description=f"{message}",
            color=discord.Color.blue()
        )
        dm_embed.set_footer(text=f"Sent by {ctx.author}")
        
        try:
            await member.send(embed=dm_embed)
            success = True
        except discord.Forbidden:
            success = False
            error_msg = await ctx.send(f"⚠️ {member.mention} has DMs turned off.", delete_after=5)

        # Log the attempt
        log_channel = self.bot.get_channel(DM_USER_BOT_LOGS)
        if log_channel:
            log_embed = discord.Embed(
                title="📨 DM Sent" if success else "🚫 DM Failed",
                color=discord.Color.green() if success else discord.Color.red()
            )
            log_embed.add_field(name="📤 Sent By", value=ctx.author.mention, inline=True)
            log_embed.add_field(name="📥 Sent To", value=member.mention if member else "Unknown", inline=True)
            log_embed.add_field(name="📝 Message", value=f"```{message if message else 'None'}```", inline=False)
            log_embed.set_footer(text=f"Command used in: {ctx.guild.name}")
            
            await log_channel.send(embed=log_embed)

    @dmuser.error
    async def dmuser_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            error_msg = await ctx.send("❌ You need Administrator permissions to use this command.", delete_after=5)
        elif isinstance(error, commands.BadArgument):
            error_msg = await ctx.send("❌ Invalid user. Please mention a valid member.", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            error_msg = await ctx.send("❌ Usage: `!dmuser @user message`", delete_after=3)
        else:
            error_msg = await ctx.send("❌ An unknown error occurred.", delete_after=5)
        
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(DMUser(bot))