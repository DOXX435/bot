import discord
from discord.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="serverinfo")
    async def server_info(self, ctx):
        guild = ctx.guild

        # Handle missing attributes safely
        owner = guild.owner.mention if guild.owner else "Unknown"
        icon_url = guild.icon.url if guild.icon else None
        banner_url = guild.banner.url if guild.banner else None

        embed = discord.Embed(
            title=f"📜 Server Info: {guild.name}",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

        # Basic Info
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=False)
        embed.add_field(name="👑 Owner", value=owner, inline=False)
        embed.add_field(name="📆 Created On", value=guild.created_at.strftime("%B %d, %Y"), inline=True)

        # **Corrected Member Stats**
        humans = sum(1 for m in guild.members if not m.bot)  # Only count non-bots
        bots = sum(1 for m in guild.members if m.bot)  # Only count bots
        embed.add_field(name="👥 Total Members", value=guild.member_count, inline=True)
        embed.add_field(name="🙎 Humans", value=humans, inline=True)
        embed.add_field(name="🤖 Bots", value=bots, inline=True)

        # Channels
        embed.add_field(name="💬 Text Channels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="🔊 Voice Channels", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="📜 Categories", value=len(guild.categories), inline=True)

        # Boosts & Features
        embed.add_field(name="🚀 Boost Level", value=f"Level {guild.premium_tier}", inline=True)
        embed.add_field(name="💎 Boost Count", value=guild.premium_subscription_count, inline=True)

        # Emojis & Stickers
        embed.add_field(name="😀 Emojis", value=f"{len(guild.emojis)}/{guild.emoji_limit}", inline=True)
        embed.add_field(name="🎟 Stickers", value=f"{len(guild.stickers)}/{guild.sticker_limit}", inline=True)

        # Top 5 Roles
        top_roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)[:5]
        role_mentions = ', '.join([role.mention for role in top_roles]) if top_roles else "None"
        embed.add_field(name="🎭 Top Roles", value=role_mentions, inline=False)

        # Security Settings
        embed.add_field(name="🔐 Verification Level", value=str(guild.verification_level), inline=True)
        embed.add_field(name="🔑 2FA Required", value="✅ Yes" if guild.mfa_level == 1 else "❌ No", inline=True)

        # Vanity URL
        vanity_url = await guild.vanity_invite() if guild.vanity_url_code else None
        embed.add_field(name="🔗 Vanity URL", value=vanity_url.url if vanity_url else "None", inline=False)

        # Bans Count (Handled Safely)
        if ctx.guild.me.guild_permissions.ban_members:
            try:
                bans = [ban async for ban in guild.bans()]
                embed.add_field(name="🚫 Banned Members", value=str(len(bans)), inline=True)
            except discord.Forbidden:
                embed.add_field(name="🚫 Banned Members", value="❌ No Permission", inline=True)
            except Exception:
                embed.add_field(name="🚫 Banned Members", value="⚠️ Error Fetching", inline=True)

        # Show Banner if available
        if banner_url:
            embed.set_image(url=banner_url)

        # Send embed & delete command message
        await ctx.send(embed=embed)
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
