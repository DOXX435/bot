import discord
from discord.ext import commands
import asyncio
from config import BAN_LOGS_CHANNEL  # Log channel from config

class BanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        await ctx.message.delete()  # Delete the command message immediately

        if not member:
            return await ctx.send("❌ **User not found or doesn't exist!**", delete_after=5)

        if not reason:
            return await ctx.send("❌ **Usage:** `!ban @user [reason]`", delete_after=5)

        if member == ctx.author:
            return await ctx.send("❌ **You can't ban yourself!**", delete_after=5)

        if member.bot:
            return await ctx.send("❌ **You can't ban a bot!**", delete_after=5)

        # **Ask for ban duration**
        duration_embed = discord.Embed(
            title="⏳ **Select Ban Duration**",
            description=(
                "📌 Please reply with one of the following durations:\n\n"
                "```▮ 1d - 1 Day\n"
                "▮ 2d - 2 Days\n"
                "▮ 5d - 5 Days\n"
                "▮ 1w - 1 Week\n"
                "▮ 2w - 2 Weeks\n"
                "▮ 1m - 1 Month\n"
                "▮ perm - Permanent Ban```"
            ),
            color=discord.Color.orange()
        )
        duration_embed.set_footer(text="Type the duration in chat (Example: 1d)")

        msg = await ctx.send(embed=duration_embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            duration_msg = await self.bot.wait_for("message", check=check, timeout=30)
            duration = duration_msg.content.lower()
            await duration_msg.delete()
        except asyncio.TimeoutError:
            return await msg.edit(content="❌ **Ban process timed out!**", embed=None, delete_after=5)

        # **Validate Duration**
        duration_map = {
            "1d": (86400, "1 Day"),
            "2d": (172800, "2 Days"),
            "5d": (432000, "5 Days"),
            "1w": (604800, "1 Week"),
            "2w": (1209600, "2 Weeks"),
            "1m": (2592000, "1 Month"),
            "perm": (None, "Permanent Ban")
        }
        ban_time, full_duration = duration_map.get(duration, (None, None))

        if full_duration is None:
            return await msg.edit(content="❌ **Invalid duration!**", embed=None, delete_after=5)

        # **Confirm Ban**
        embed = discord.Embed(title="✅ **User Banned Successfully**", color=discord.Color.green())
        embed.add_field(name="👤 **User**", value=f"{member.mention} (`{member.id}`)", inline=True)
        embed.add_field(name="🛑 **Banned By**", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=True)
        embed.add_field(name="📜 **Reason**", value=f"```{reason}```", inline=False)
        embed.add_field(name="⌛ **Duration**", value=f"```{full_duration}```", inline=True)

        # **Show Roles of User Being Banned**
        member_roles = ", ".join([role.mention for role in member.roles if role.name != "@everyone"]) or "`No Roles`"
        embed.add_field(name="🎭 **User Roles**", value=member_roles, inline=False)

        await msg.edit(content="", embed=embed)

        # **DM User**
        try:
            dm_embed = discord.Embed(title="⛔ **You Have Been Banned**", color=discord.Color.red())
            dm_embed.add_field(name="📜 **Reason**", value=f"```{reason}```", inline=False)
            dm_embed.add_field(name="⌛ **Duration**", value=f"```{full_duration}```", inline=True)
            dm_embed.add_field(name="👮 **Banned By**", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=True)
            dm_embed.add_field(name="🏛️ **Server**", value=f"{ctx.guild.name}", inline=True)
            dm_embed.set_footer(text="Contact the server staff if you believe this was a mistake.")
            await member.send(embed=dm_embed)
        except:
            await ctx.send(f"⚠️ **{member.mention} has DMs turned off.**", delete_after=5)

        # **Ban User**
        try:
            await member.ban(reason=reason)
        except discord.Forbidden:
            return await ctx.send(f"❌ **I don't have permission to ban {member.mention}!**", delete_after=5)

        # **Log Ban in Server**
        log_channel = self.bot.get_channel(BAN_LOGS_CHANNEL)
        if log_channel:
            log_embed = discord.Embed(title="🔨 **Ban Log**", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            log_embed.add_field(name="👤 **User**", value=f"{member.mention} (`{member.id}`)", inline=True)
            log_embed.add_field(name="📜 **Reason**", value=f"```{reason}```", inline=False)
            log_embed.add_field(name="⌛ **Duration**", value=f"```{full_duration}```", inline=True)
            log_embed.add_field(name="👮 **Banned By**", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=True)

            # **Show Moderator's Roles**
            mod_roles = ", ".join([role.mention for role in ctx.author.roles if role.name != "@everyone"]) or "`No Roles`"
            log_embed.add_field(name="🔧 **Moderator Roles**", value=mod_roles, inline=False)

            # **Show User's Roles Before Ban**
            log_embed.add_field(name="🎭 **User's Roles Before Ban**", value=member_roles, inline=False)

            log_embed.set_footer(text=f"Server: {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            await log_channel.send(embed=log_embed)

        # **Unban after time (if not permanent)**
        if ban_time:
            await asyncio.sleep(ban_time)
            await ctx.guild.unban(member, reason="Ban duration expired")
            await ctx.send(f"✅ **{member.mention} has been unbanned.**", delete_after=5)

async def setup(bot):
    await bot.add_cog(BanCommand(bot))
