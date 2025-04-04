import discord
from discord.ext import commands

class BotCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def botcommands(self, ctx):
        """
        Sends an embed with all available bot commands, categorized, and deletes the command message.
        """

        # Delete the original message
        await ctx.message.delete()

        embed = discord.Embed(
            title="🤖 **Bot Command List**",
            description="Here are all the available bot commands, categorized for easy use.\n\n"
                        "🔹 **Use the commands exactly as shown**\n"
                        "🔹 **Some commands may require specific permissions**",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)  # Server icon
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

        # 🔨 MODERATION COMMANDS
        embed.add_field(
            name="🔨 **Moderation Commands**",
            value=(
                "🔹 **`!ban @user [reason]`** → bans user from the server.\n"
                "🔹 **`!kick @user [reason]`** → Kick a user from the server.\n"
                "🔹 **`!unban @user [reason]`** → unbans a user.\n"
                "🔹 **`!bannedusers`** → shows **all banned** users .\n"
                "🔹 **`!purge`** → Deletes **all messages** in a channel.\n"
                "🔹 **`!delete [number]`** → Deletes a specific number of messages.\n"
                "🔹 **`!giverole  @user`** → give user a role.\n"
            ),
            inline=False
        )

        # ℹ️ INFORMATION COMMANDS
        embed.add_field(
            name="ℹ️ **Info Commands and other stuff**",
            value=(
                "🔹 **`!userinfo @user`** → Shows detailed info about a user.\n"
                "🔹 **`!botstatus`** → Shows detailed info about the bot.\n"
                "🔹 **`!serverinfo`** → Shows everthing about the server.\n"
                "🔹 **`!dmuser @user [message]`** → sends a custom message\n"
            ),
            inline=False
        )

        # 🎭 MISCELLANEOUS COMMANDS
        embed.add_field(
            name=" 🎭 ** "
            "🤖 **__bot features__** ",
            value=(
                "🔹💥 **anti spam system** \n"
                "🔹🗒️ **logging system** \n"
            ),
            inline=False
        )

        await ctx.send(embed=embed)

# Async setup function to load the cog
async def setup(bot):
    await bot.add_cog(BotCommand(bot))
