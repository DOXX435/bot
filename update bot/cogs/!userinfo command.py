import discord
from discord.ext import commands
import datetime

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        await ctx.message.delete()  # Delete the original command message first

        # Check if user has the required role
        mod_role = discord.utils.get(ctx.guild.roles, name="Mod")
        if not mod_role or mod_role.position > ctx.author.top_role.position:
            await ctx.send("❌ **You need the `Mod` role or higher to use this command!**", delete_after=5)
            return

        if member is None:
            await ctx.send("❌ **Usage:** `!userinfo @User`\nℹ️ **You must mention a valid user!**", delete_after=5)
            return

        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        roles = roles if roles else "None"

        # Format permissions neatly
        perm_names = [perm[0].replace('_', ' ').title() for perm in member.guild_permissions if perm[1]]
        perm_text = ', '.join(perm_names[:5]) + ('...' if len(perm_names) > 5 else '')

        embed = discord.Embed(
            title=f"👤 **User Information**",
            description=f"ℹ️ Showing info for {member.mention}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )

        embed.set_thumbnail(url=member.avatar.url if member.avatar else "https://cdn.discordapp.com/embed/avatars/0.png")

        embed.add_field(name="🆔 **User ID**", value=f"```{member.id}```", inline=True)
        embed.add_field(name="🔤 **Username**", value=f"```{member.name}```", inline=True)
        embed.add_field(name="🏷️ **Nickname**", value=f"```{member.nick if member.nick else 'None'}```", inline=False)

        embed.add_field(name="📅 **Account Created**", value=f"```{member.created_at.strftime('%Y-%m-%d %H:%M:%S')}```", inline=True)
        embed.add_field(name="📆 **Joined Server**", value=f"```{member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}```", inline=True)

        embed.add_field(name="🔰 **Roles**", value=f"{', '.join(roles)}", inline=False)
        embed.add_field(name="⚖️ **Top Role**", value=f"{member.top_role.mention}", inline=True)
        embed.add_field(name="🔨 **Key Permissions**", value=f"```{perm_text}```", inline=False)

        embed.add_field(name="💠 **Status**", value=f"```{member.status}```", inline=True)
        embed.add_field(name="🎮 **Activity**", value=f"```{member.activity.name if member.activity else 'None'}```", inline=True)

        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))
