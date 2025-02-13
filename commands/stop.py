import discord
from discord.ext import commands
from .queue_manager import current_player, queue

class StopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="정지")
    async def stop(self, ctx):
        global current_player
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        
        if voice_client and voice_client.is_connected():
            embed = discord.Embed(title="⏹️ 정지", description="음악을 멈추고 봇이 나갈게요! 대기열도 모두 삭제돼요.", color=discord.Color.red())
            await voice_client.disconnect()
            await ctx.send(embed=embed)
            current_player = None
            queue.clear()  # 대기열도 초기화
        else:
            embed = discord.Embed(title="❗정지 실패", description="봇이 음성 채널에 있지 않아요.", color=discord.Color.red())
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StopCommand(bot))