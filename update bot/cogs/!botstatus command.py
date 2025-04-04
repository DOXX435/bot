import discord
from discord.ext import commands
import psutil
import platform
import datetime

class BotStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def botstatus(self, ctx):
        await ctx.message.delete()  # Delete the original command message first

        # Check if user has the required role
        mod_role = discord.utils.get(ctx.guild.roles, name="Mod")
        if not mod_role or mod_role.position > ctx.author.top_role.position:
            await ctx.send("❌ **You need the `Mod` role or higher to use this command!**", delete_after=5)
            return

        bot_user = self.bot.user
        uptime = datetime.datetime.now() - self.bot.start_time
        uptime_str = str(uptime).split('.')[0]
        guild_count = len(self.bot.guilds)
        command_count = len(self.bot.commands)

        def progress_bar(percentage):
            total_blocks = 10
            filled_blocks = round((percentage / 100) * total_blocks)
            empty_blocks = total_blocks - filled_blocks
            return "🟩" * filled_blocks + "⬜" * empty_blocks

        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        thread_count = psutil.cpu_count()

        embed = discord.Embed(
            title="💬 **Bot Status**",
            description="🔵 **Online & Fully Operational!**",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )

        embed.add_field(name="🤖 **Bot Name**", value=f"```{bot_user.name}```", inline=True)
        embed.add_field(name="🆔 **Bot ID**", value=f"```{bot_user.id}```", inline=True)
        embed.add_field(name="🕒 **Uptime**", value=f"```{uptime_str}```", inline=False)

        embed.add_field(name="⚡ **Latency**", value=f"```{round(self.bot.latency * 1000)} ms```", inline=True)
        embed.add_field(name="📜 **Bot Version**", value="```1.0.0```", inline=True)
        embed.add_field(name="🌎 **Guilds Count**", value=f"```{guild_count} Servers```", inline=True)
        embed.add_field(name="🛠 **Commands Count**", value=f"```{command_count} Commands```", inline=True)

        embed.add_field(name="🐍 **Python Version**", value=f"```{platform.python_version()}```", inline=True)
        embed.add_field(name="📚 **Library**", value="```discord.py```", inline=True)
        embed.add_field(name="💾 **Operating System**", value=f"```{platform.system()} {platform.release()}```", inline=False)

        embed.add_field(name="⚙️ **Processor**", value=f"```{platform.processor()}```", inline=False)
        embed.add_field(name="🧵 **CPU Threads**", value=f"```{thread_count}```", inline=True)

        embed.add_field(name="🧠 **CPU Usage**", value=f"```{cpu_usage}%``` {progress_bar(cpu_usage)}", inline=False)
        embed.add_field(name="🔋 **Memory Usage**", value=f"```{memory_usage}%``` {progress_bar(memory_usage)}", inline=False)
        embed.add_field(name="💽 **Disk Usage**", value=f"```{disk_usage}%``` {progress_bar(disk_usage)}", inline=False)

        embed.add_field(name="🛠 **Loaded Cogs**", value=f"```{', '.join(self.bot.cogs.keys())}```", inline=False)

        embed.set_thumbnail(url=bot_user.avatar.url if bot_user.avatar else "https://cdn.discordapp.com/embed/avatars/0.png")
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    bot.start_time = datetime.datetime.now()
    await bot.add_cog(BotStatus(bot))
