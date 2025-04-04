import discord
from discord.ext import commands
from config import GIVE_ROLE_LOGS

class GiveRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_selection = {}

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def giverole(self, ctx, member: discord.Member = None):
        """Lists available roles and assigns one based on user selection."""

        # Delete the original command message
        await ctx.message.delete()

        # Check if a member was mentioned
        if not member:
            error_msg = await ctx.send("❌ Usage: `!giverole @user`", delete_after=5)
            return

        # Get the bot’s highest role
        bot_highest_role = max(ctx.guild.me.roles, key=lambda r: r.position)

        # Get roles below the bot's highest role
        available_roles = [r for r in ctx.guild.roles if r.position < bot_highest_role.position and not r.is_default()]
        available_roles.sort(key=lambda r: r.position, reverse=True)  # Sort roles from highest to lowest

        # Store role selection for this user
        self.role_selection[ctx.author.id] = available_roles

        # Check if the user has admin permissions
        admin_status_member = "✅ **Admin**" if member.guild_permissions.administrator else "❌ **Not Admin**"
        admin_status_author = "✅ **Admin**" if ctx.author.guild_permissions.administrator else "❌ **Not Admin**"

        # Get all roles as mentions
        member_roles = ", ".join([r.mention for r in member.roles if not r.is_default()]) or "No roles"
        author_roles = ", ".join([r.mention for r in ctx.author.roles if not r.is_default()]) or "No roles"

        # Generate role list with numbers, splitting into chunks of 15
        role_chunks = [available_roles[i:i+15] for i in range(0, len(available_roles), 15)]
        embed_messages = []

        for index, chunk in enumerate(role_chunks):
            role_list = "\n".join(
                [f"`{i+1+(index*15)}.` {role.mention} {'✅' if role.permissions.administrator else '❌'}" for i, role in enumerate(chunk)]
            )

            embed = discord.Embed(
                title="🎭 Available Roles",
                description=f"Select a role for {member.mention} by typing the corresponding number.\n\n{role_list}",
                color=discord.Color.blue()
            )
            embed.add_field(name="👤 User", value=f"{member.mention} ({admin_status_member})", inline=True)
            embed.add_field(name="🛡️ Admin?", value=f"{admin_status_author} (You)", inline=True)
            embed.set_footer(text="✅ = Has Admin, ❌ = No Admin\nType the number of the role to assign.")

            embed_msg = await ctx.send(embed=embed)
            embed_messages.append(embed_msg)

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.isdigit()

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30)
            role_index = int(msg.content) - 1

            # Delete the user's response
            await msg.delete()

            # Check if role index is valid
            if 0 <= role_index < len(available_roles):
                role = available_roles[role_index]

                # Check if the user already has the role
                if role in member.roles:
                    already_has_role_msg = await ctx.send(f"⚠️ {member.mention} already has the {role.mention} role.", delete_after=5)
                    await self.cleanup(embed_messages)  # Deletes role selection embeds
                    return  # Stop execution here to prevent logging and success message

                await member.add_roles(role)

                # Success embed
                success_embed = discord.Embed(
                    title="✅ Role Assigned",
                    description=f"{member.mention} has been given the {role.mention} role.",
                    color=discord.Color.green()
                )
                success_msg = await ctx.send(embed=success_embed, delete_after=5)

                # Log the role assignment **only if successful**
                log_channel = self.bot.get_channel(GIVE_ROLE_LOGS)
                if log_channel:
                    log_embed = discord.Embed(
                        title="📜 Role Assignment Log",
                        color=discord.Color.blue()
                    )
                    log_embed.add_field(name="👤 **User Assigned**", value=f"{member.mention} ({admin_status_member})", inline=False)
                    log_embed.add_field(name="📜 **Their Roles Before**", value=f"{member_roles}", inline=False)
                    log_embed.add_field(name="🎭 **Role Given**", value=f"{role.mention}", inline=False)
                    log_embed.add_field(name="🔧 **Assigned By**", value=f"{ctx.author.mention} ({admin_status_author})", inline=False)
                    log_embed.add_field(name="📜 **Their Roles**", value=f"{author_roles}", inline=False)
                    log_embed.set_thumbnail(url=member.avatar.url)
                    log_embed.set_footer(text="✅ = Has Admin | ❌ = Not Admin")

                    await log_channel.send(embed=log_embed)

                # Cleanup embeds
                await self.cleanup(embed_messages)

        except Exception:
            await self.cleanup(embed_messages)

    async def cleanup(self, messages):
        """Deletes the bot's role selection messages."""
        for msg in messages:
            try:
                await msg.delete()
            except discord.NotFound:
                pass  # Ignore if the message was already deleted

async def setup(bot):
    await bot.add_cog(GiveRole(bot))
