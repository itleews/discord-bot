import discord
from discord.ext import commands
import asyncio
import os
import googleapiclient.discovery

from dotenv import load_dotenv  # API 키 보안 관리
from .queue_manager import queue, current_player

# 환경 변수 로드
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# FFmpeg 옵션
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# YouTube API 검색 함수
def search_youtube(query):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=1,
        type="video"
    )
    response = request.execute()

    if "items" in response and len(response["items"]) > 0:
        video = response["items"][0]
        video_id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return {"title": title, "url": video_url, "thumbnail": thumbnail}
    else:
        return None

# 음성 재생 클래스
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options), data={"url": url})

# 다음 곡 재생 함수
def play_next(ctx):
    global current_player
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    
    if queue:
        current_player = queue.pop(0)
        voice_client.play(current_player, after=lambda e: play_next(ctx))

        embed = discord.Embed(title=f"🎵 {current_player.title}", color=discord.Color.blue())
        embed.add_field(name="영상", value=f"[링크]({current_player.url})", inline=True)
        embed.set_thumbnail(url=current_player.thumbnail)
        asyncio.run_coroutine_threadsafe(ctx.send(embed=embed), ctx.bot.loop)

# 음악 재생 명령어
class PlayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="재생")
    async def play(self, ctx, *, query: str):
        if not ctx.message.author.voice:
            await ctx.send(embed=discord.Embed(title="❗재생 실패", description="먼저 음성 채널에 입장하세요.", color=discord.Color.red()))
            return

        channel = ctx.message.author.voice.channel
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if not voice_client:
            try:
                voice_client = await channel.connect()
            except Exception as e:
                await ctx.send(embed=discord.Embed(title="❗오류", description="음성 채널 연결에 실패했어요.", color=discord.Color.red()))
                return

        # 유튜브 검색 및 URL 가져오기
        searched_by = ctx.message.author
        embed = discord.Embed(title="🔍 유튜브 검색 중...", color=discord.Color.green())
        embed.add_field(name=query, value="노래를 검색 중이에요.", inline=False)
        embed.set_author(name=f"{searched_by.name}", icon_url=searched_by.avatar.url)
        search_message = await ctx.send(embed=embed)

        video_info = search_youtube(query)
        if not video_info:
            await ctx.send(embed=discord.Embed(title="❗오류", description="유튜브에서 검색 결과를 찾을 수 없어요.", color=discord.Color.red()))
            return
        
        player = await YTDLSource.from_url(video_info["url"], loop=ctx.bot.loop)
        player.title = video_info["title"]
        player.url = video_info["url"]
        player.thumbnail = video_info["thumbnail"]
        queue.append(player)

        if not voice_client.is_playing():
            global current_player
            current_player = queue.pop(0)
            voice_client.play(current_player, after=lambda e: play_next(ctx))

        await search_message.delete()

        embed = discord.Embed(title=f"🎵 {player.title}", color=discord.Color.blue())
        embed.add_field(name="영상", value=f"[링크]({player.url})", inline=True) 
        embed.set_thumbnail(url=player.thumbnail)
        embed.set_author(name=f"{searched_by.name}", icon_url=searched_by.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PlayCommand(bot))
