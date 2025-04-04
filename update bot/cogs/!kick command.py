import discord
from discord.ext import commands
from discord import Embed
from datetime import datetime

# Import config where KICK_LOGS_CHANNEL is stored
from config import KICK_LOGS_CHANNEL  # Update this path if needed

class KickCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        """
        Kicks a user, deletes the command message, sends them a DM before removal, and logs the action.
        """
        try:
            await ctx.message.delete()  # 🚨 Deletes the command message immediately
        except discord.Forbidden:
            pass  # Bot doesn't have permission to delete messages (fails silently)

        # Check if the command is used correctly
        if reason is None:
            await ctx.send("⚠️ **You must provide a reason for the kick!**\nExample: `!kick @User Spamming`")
            return

        # Prevent self-kick and bot kick
        if member == ctx.author:
            await ctx.send("🚫 **You cannot kick yourself!**")
            return
        if member.bot:
            await ctx.send("🚫 **You cannot kick a bot!**")
            return

        # Get all roles of the member being kicked & the person kicking them
        kicked_roles = [role.mention for role in member.roles if role != ctx.guild.default_role]  # Exclude @everyone
        kicker_roles = [role.mention for role in ctx.author.roles if role != ctx.guild.default_role]  # Exclude @everyone
        
        kicked_roles_str = ", ".join(kicked_roles) if kicked_roles else "None"
        kicker_roles_str = ", ".join(kicker_roles) if kicker_roles else "None"

        # Get kicker's avatar & server icon
        kicker_avatar = ctx.author.avatar.url if ctx.author.avatar else discord.Embed.Empty
        server_icon = ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty

        # 📩 DM the user before kicking
        try:
            dm_embed = Embed(
                title="🚨 You've Been Kicked!",
                description=f"Hello {member.mention}, you have been **removed** from **{ctx.guild.name}**.",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            dm_embed.set_thumbnail(url=server_icon)  # Server icon
            dm_embed.set_author(name=f"Kicked by {ctx.author.name}", icon_url=kicker_avatar)  # Kicker's info
            
            dm_embed.add_field(name="📜 **Reason**", value=f"```{reason}```", inline=False)
            dm_embed.add_field(name="🌍 **Server**", value=f"{ctx.guild.name}", inline=True)
            dm_embed.add_field(name="🔨 **Kicked By**", value=ctx.author.mention, inline=True)
            dm_embed.add_field(name="🕒 **Time**", value=f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", inline=False)
            
            dm_embed.set_footer(text="If you believe this was a mistake, contact a server moderator.")
            
            await member.send(embed=dm_embed)

        except discord.Forbidden:
            pass  # User has DMs disabled

        # 🦵 Kick the member
        await member.kick(reason=reason)

        # ✅ Success message in the channel
        embed = Embed(
            title="✅ User Kicked",
            description=f"{member.mention} has been kicked from the server.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="⚙️ Reason", value=f"```{reason}```", inline=False)
        embed.add_field(name="🔨 Kicked by", value=ctx.author.mention, inline=True)
        embed.add_field(name="👥 Kicked User", value=member.mention, inline=True)
        success_msg = await ctx.send(embed=embed)
        
        # ⏳ Auto-delete success message after 5 seconds (optional)
        await success_msg.delete(delay=5)

        # 📝 Log the kick in the specified channel
        log_channel = self.bot.get_channel(KICK_LOGS_CHANNEL)
        if log_channel:
            log_embed = Embed(
                title="🚨 User Kicked",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            log_embed.set_thumbnail(url=server_icon)  # Server icon
            
            log_embed.add_field(name="🔨 **Kicked By**", value=f"{ctx.author.mention} ({ctx.author.id})", inline=False)
            log_embed.add_field(name="👥 **Kicked User**", value=f"{member.mention} ({member.id})", inline=False)
            log_embed.add_field(name="📜 **Reason**", value=f"```{reason}```", inline=False)
            log_embed.add_field(name="📍 **Channel**", value=ctx.channel.mention, inline=False)
            log_embed.add_field(name="🌍 **Server**", value=f"{ctx.guild.name}", inline=False)
            log_embed.add_field(name="🕒 **Time**", value=f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", inline=False)
            log_embed.add_field(name="👑 **Kicker Roles**", value=kicker_roles_str, inline=False)
            log_embed.add_field(name="🚷 **Kicked User Roles**", value=kicked_roles_str, inline=False)

            await log_channel.send(embed=log_embed)

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("🚫 **You do not have permission to kick members.**", delete_after=5)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ **Invalid member mentioned!**\nExample: `!kick @User Spamming`", delete_after=5)
        else:
            await ctx.send(f"⚠️ **An unexpected error occurred:** {error}", delete_after=5)

# Async setup function to load the cog
async def setup(bot):
    await bot.add_cog(KickCommand(bot))
