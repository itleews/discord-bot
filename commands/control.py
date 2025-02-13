import discord
from discord.ext import commands
from .play import queue, play_next

class ControlCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="일시정지")
    async def pause(self, ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            embed = discord.Embed(title="⏸️일시정지", description="음악을 일시 정지해요.", color=discord.Color.orange())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="❗일시정지 실패", description="현재 재생 중인 음악이 없어요.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="재개")
    async def resume(self, ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            embed = discord.Embed(title="▶️ 재개", description="음악을 계속 재생할게요.", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="❗재개 실패", description="현재 일시 정지된 음악이 없어요.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="다음")
    async def skip(self, ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            embed = discord.Embed(title="⏭️다음 곡 재생", description="현재 곡을 건너뛰고 다음 곡으로 넘어갈게요.", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="❗다음 곡 재생 실패", description="재생 중인 곡이 없어요.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="삭제")
    async def remove(self, ctx, index: int):
        if 0 < index <= len(queue):
            removed = queue.pop(index - 1)
            embed = discord.Embed(title="🗑️삭제 완료", description=f"{index}. {removed.title}을(를) 대기열에서 삭제했어요.", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="❗삭제 실패", description="잘못된 번호예요. 대기열에 있는 번호를 입력해주세요.", color=discord.Color.red())
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ControlCommand(bot))