import discord
from discord.ext import commands
import asyncio

class BannedUsers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bannedusers(self, ctx):
        """
        Displays a list of all banned users and their ban reasons.
        Checks if the user has the required permission (administrator).
        """

        # Check if the user has administrator permission
        if not ctx.author.guild_permissions.administrator:
            # Send a message saying they don't have permission
            no_permission_embed = discord.Embed(
                title="❌ **No Permission**",
                description="You need **Administrator** permissions to use this command.",
                color=discord.Color.red()
            )

            # Send the no permission embed
            no_permission_message = await ctx.send(embed=no_permission_embed)

            # Wait 3 seconds before deleting the command and no permission message
            await asyncio.sleep(3)

            # Delete the user's command message
            await ctx.message.delete()

            # Delete the no permission message
            await no_permission_message.delete()

            return  # Exit the function if no permission

        # Fetch all banned users (using async for since it's an async generator)
        banned_users = [entry async for entry in ctx.guild.bans()]

        if not banned_users:
            return await ctx.send(embed=discord.Embed(
                title="🚫 No Banned Users",
                description="There are currently no banned users in this server.",
                color=discord.Color.red()
            ))

        # Split the banned users into chunks of 15
        chunks = [banned_users[i:i + 15] for i in range(0, len(banned_users), 15)]

        # Loop through the chunks and create a new embed for each chunk
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title="🚫 **Banned Users List**",
                description=f"Here are the banned users in **{ctx.guild.name}** (Page {i + 1}/{len(chunks)}):",
                color=discord.Color.dark_red()
            )

            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)  # Server icon
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

            # Add each banned user to the embed
            for entry in chunk:
                user = entry.user
                reason = entry.reason if entry.reason else "No reason provided"
                
                # Using black bars for the user ID and reason
                embed.add_field(
                    name=f"**{user.name}#{user.discriminator}** (ID: `||{user.id}||`)",
                    value=f"📝 **Reason:** `||{reason}||`",
                    inline=False
                )

            await ctx.send(embed=embed)

# Async setup function to load the cog
async def setup(bot):
    await bot.add_cog(BannedUsers(bot))
