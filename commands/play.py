import discord
from discord.ext import commands
from youtube_api import search_youtube  # YouTube API로 비디오 정보 가져오기
import asyncio

queue = []

class PlayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="재생")
    async def play(self, ctx, *, query: str):
        if not ctx.message.author.voice:
            embed = discord.Embed(title="❗재생 실패", description="먼저 음성 채널에 입장하세요.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        channel = ctx.message.author.voice.channel
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if not voice_client:
            try:
                voice_client = await channel.connect()
            except Exception as e:
                embed = discord.Embed(title="❗오류", description="음성 채널 연결에 실패했어요.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

        # 유튜브에서 비디오 정보 가져오기
        video_info = search_youtube(query)
        if not video_info:
            embed = discord.Embed(title="❗오류", description="검색된 영상이 없어요.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        # 비디오 URL을 사용하여 오디오 스트리밍 시작
        player = discord.FFmpegPCMAudio(video_info["url"])
        queue.append(player)

        if not voice_client.is_playing():
            voice_client.play(player, after=lambda e: play_next(ctx))

        # 곡 정보 반환
        embed = discord.Embed(
            title=f"🎵 {video_info['title']}",
            color=discord.Color.blue()
        )
        embed.add_field(name="영상", value=f"[링크]({video_info['url']})", inline=True)
        embed.set_thumbnail(url=video_info['thumbnail'])
        await ctx.send(embed=embed)

def play_next(ctx):
    if queue:
        player = queue.pop(0)
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        voice_client.play(player, after=lambda e: play_next(ctx))
