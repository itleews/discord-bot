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
        self.info = data  # self.info를 data로 설정
        self.title = data.get('title')
        self.url = data.get('webpage_url')
        self.thumbnail = data.get('thumbnail')  # 썸네일 URL 추가

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

queue = []
current_player = None

# 봇이 명령어를 받으면 실행하는 부분
@bot.command(name="재생")
async def play(ctx, *, query: str):
    global current_player, current_message
    if not ctx.message.author.voice:
        embed = discord.Embed(title="재생 실패", description="먼저 음성 채널에 입장해야 합니다.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    channel = ctx.message.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        voice_client = await channel.connect()
    
    searched_by = ctx.message.author

    embed = discord.Embed(title="🔍 검색", color=discord.Color.green())
    embed.add_field(name=query, value="검색 중...", inline=False)
    embed.set_author(name=f"{searched_by.name}", icon_url=searched_by.avatar.url)
    search_message = await ctx.send(embed=embed)

    async with ctx.typing():
        player = await YTDLSource.from_url(f"ytsearch:{query}", loop=bot.loop, stream=True)
        queue.append(player)
        if not voice_client.is_playing():
            current_player = queue.pop(0)
            voice_client.play(current_player, after=lambda e: play_next(ctx))
    
    await search_message.delete()

    # 곡 길이 가져오기
    duration_seconds = player.info['duration']
    minutes, seconds = divmod(duration_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"

    # 대기열 형식
    queue_info = '지금 재생' if not queue else ', '.join(str(i+1) for i in range(len(queue)))

    # 재생한 사람 정보 추가
    played_by = ctx.message.author  # 재생한 사람의 이름

    # 테이블 형식으로 정보 정리
    embed = discord.Embed(
        title=f"🎵 {player.title}",
        color=discord.Color.blue()
    )
    embed.add_field(name="재생 시간", value=formatted_duration, inline=True)
    embed.add_field(name="대기열", value=queue_info, inline=True)
    embed.add_field(name="영상", value=f"[링크]({player.url})", inline=True) 
    embed.set_thumbnail(url=player.thumbnail)  # 이미지 크기를 작게 표시
    embed.set_author(name=f"{played_by.name}", icon_url=played_by.avatar.url)  # 작성자 정보 추가
    if queue_info != '지금 재생':
        embed.set_footer(text="➕ 대기열에 곡을 추가합니다.")

    current_message = await ctx.send(embed=embed)

def play_next(ctx):
    global current_player
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if queue:
        current_player = queue.pop(0)
        voice_client.play(current_player, after=lambda e: play_next(ctx))

        # 곡 길이 가져오기
        duration_seconds = current_player.info['duration']
        minutes, seconds = divmod(duration_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"

        # 대기열 형식
        queue_info = '지금 재생' if not queue else ', '.join(str(i+1) for i in range(len(queue)))

        # 재생한 사람 정보 추가
        played_by = ctx.message.author  # 재생한 사람의 이름

        # 테이블 형식으로 정보 정리
        embed = discord.Embed(
            title=f"🎵 {current_player.title}",
            color=discord.Color.blue()
        )
        embed.add_field(name="재생 시간", value=formatted_duration, inline=True)
        embed.add_field(name="대기열", value=queue_info, inline=True)
        embed.add_field(name="영상", value=f"[링크]({current_player.url})", inline=True)
        embed.set_thumbnail(url=current_player.thumbnail)  # 이미지 크기를 작게 표시
        embed.set_footer(text=f"{played_by.name}#{played_by.discriminator}", icon_url=played_by.avatar.url)  # 작성자 정보 추가

        asyncio.run_coroutine_threadsafe(ctx.send(embed=embed), bot.loop)

@bot.command(name="정지")
async def stop(ctx):
    global current_player
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    if voice_client and voice_client.is_connected():
        embed = discord.Embed(title="정지", description="음악을 멈추고 봇이 퇴장합니다.", color=discord.Color.red())
        await voice_client.disconnect()
        await ctx.send(embed=embed)
        current_player = None
    else:
        embed = discord.Embed(title="정지 실패", description="봇이 음성 채널에 있지 않습니다.", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name="일시정지")
async def pause(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        embed = discord.Embed(title="일시정지", description="음악을 일시 정지합니다.", color=discord.Color.orange())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="일시정지 실패", description="현재 재생 중인 음악이 없습니다.", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name="다시재생")
async def resume(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        embed = discord.Embed(title="다시재생", description="음악을 다시 재생합니다.", color=discord.Color.green())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="다시재생 실패", description="현재 일시 정지된 음악이 없습니다.", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name="현재재생")
async def now_playing(ctx):
    global current_player
    if current_player:
        embed = discord.Embed(title="현재 재생 중", description=f"[{current_player.title}]({current_player.url})", color=discord.Color.blue())
        embed.set_image(url=current_player.thumbnail)  # 이미지 추가
        await ctx.send(embed=embed)
    else:
        await ctx.send("현재 재생 중인 음악이 없습니다.")

@bot.command(name="대기열초기화")
async def clear_queue(ctx):
    global queue
    queue = []
    embed = discord.Embed(title="대기열 초기화", description="대기열이 초기화되었습니다.", color=discord.Color.green())
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
        embed = discord.Embed(title="스킵", description="현재 재생 중인 노래를 스킵합니다.", color=discord.Color.green())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="스킵 실패", description="현재 재생 중인 노래가 없습니다.", color=discord.Color.red())
        await ctx.send(embed=embed)

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
    embed = discord.Embed(title="춘식이 명령어 리스트", description="""  
    **!재생 [URL 또는 검색어]** - 음악을 재생합니다.
    **!정지** - 음악을 멈추고 봇이 음성 채널에서 퇴장합니다.
    **!대기열** - 현재 대기열을 표시합니다.
    **!스킵** - 현재 재생 중인 노래를 스킵합니다.
    **!삭제 [번호]** - 대기열에서 특정 번호의 노래를 삭제합니다.
    **!명령어** - 사용 가능한 명령어 리스트를 표시합니다.
    **!일시정지** - 현재 재생 중인 음악을 일시 정지합니다.
    **!다시재생** - 일시 정지된 음악을 다시 재생합니다.
    **!현재재생** - 현재 재생 중인 음악을 표시합니다.
    **!대기열초기화** - 대기열을 초기화합니다.
    """, color=discord.Color.blue())
    await ctx.send(embed=embed)

# 토큰으로 봇 실행
bot.run(token)
