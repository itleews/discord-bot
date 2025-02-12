import discord
from discord.ext import commands
import yt_dlp
import asyncio

from bot_token import token

intents = discord.Intents.default()
intents.message_content = True  # 메시지 읽기 권한
bot = commands.Bot(command_prefix="!", intents=intents)

# 유튜브 DL 옵션
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6로 인한 문제 방지
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

queue = []

# 봇이 명령어를 받으면 실행하는 부분
@bot.command(name="실행")
async def play(ctx, *, query: str):
    if not ctx.message.author.voice:
        embed = discord.Embed(title="실행 실패", description="먼저 음성 채널에 입장해야 합니다.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    channel = ctx.message.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        voice_client = await channel.connect()

    embed = discord.Embed(title="검색 중", description=f"'{query}' 검색 중...", color=discord.Color.green())
    search_message = await ctx.send(embed=embed)

    async with ctx.typing():
        player = await YTDLSource.from_url(f"ytsearch:{query}", loop=bot.loop, stream=True)
        queue.append(player)
        if not voice_client.is_playing():
            voice_client.play(queue.pop(0), after=lambda e: play_next(ctx))
    
    await search_message.delete()
    embed = discord.Embed(title="재생 중", description=f"[{player.title}]({player.url})", color=discord.Color.blue())
    await ctx.send(embed=embed)

def play_next(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if queue:
        voice_client.play(queue.pop(0), after=lambda e: play_next(ctx))

@bot.command(name="정지")
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    if voice_client and voice_client.is_connected():
        embed = discord.Embed(title="정지", description="음악을 멈추고 봇이 퇴장합니다.", color=discord.Color.red())
        await voice_client.disconnect()
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="정지 실패", description="봇이 음성 채널에 있지 않습니다.", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name="대기열")
async def queue_list(ctx):
    if queue:
        embed = discord.Embed(title="대기열", description="\n".join([f"{i+1}. {track.title}" for i, track in enumerate(queue)]), color=discord.Color.blue())
    else:
        embed = discord.Embed(title="대기열", description="대기열이 비어 있습니다.", color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command(name="스킵")
async def skip(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("현재 재생 중인 노래를 스킵합니다.")
    else:
        await ctx.send("현재 재생 중인 노래가 없습니다.")

@bot.command(name="삭제")
async def remove(ctx, index: int):
    if 0 < index <= len(queue):
        removed = queue.pop(index - 1)
        embed = discord.Embed(title="삭제 완료", description=f"{index}. {removed.title}을(를) 대기열에서 삭제했습니다.", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="삭제 실패", description="유효한 대기열 번호를 입력하세요.", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name="명령어")
async def commands_list(ctx):
    embed = discord.Embed(title="명령어 리스트", description="""
    **!실행 [URL 또는 검색어]** - 음악을 재생합니다.
    **!정지** - 음악을 멈추고 봇이 음성 채널에서 퇴장합니다.
    **!대기열** - 현재 대기열을 표시합니다.
    **!스킵** - 현재 재생 중인 노래를 스킵합니다.
    **!삭제 [번호]** - 대기열에서 특정 번호의 노래를 삭제합니다.
    **!명령어** - 사용 가능한 명령어 리스트를 표시합니다.
    """, color=discord.Color.blue())
    await ctx.send(embed=embed)

# 토큰으로 봇 실행
bot.run(token)