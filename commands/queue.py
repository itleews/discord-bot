import discord
from discord.ext import commands
from .queue_manager import queue, current_player

class QueueCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="대기열")
    async def queue(self, ctx):
        if len(queue) == 0:
            embed = discord.Embed(title="📜 대기열", description="대기열에 아무 노래도 없어요", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="📜 대기열", description="대기 중인 노래들이에요", color=discord.Color.blue())
            for i, song in enumerate(queue):
                embed.add_field(name=f"{i + 1}번", value=f"[{song.title}]({song.url})", inline=False)
            await ctx.send(embed=embed)

    @commands.command(name="대기열삭제")
    async def clear_queue(self, ctx):
        global queue
        queue.clear()
        embed = discord.Embed(title="🗑️ 대기열 삭제", description="대기열에 있는 모든 노래를 삭제했어요.", color=discord.Color.green())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(QueueCommand(bot))