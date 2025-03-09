import discord
from discord.ext import commands
import asyncio
from youtube_api import get_video_url  # 유튜브 API에서 비디오 URL 가져오기
import youtube_dl  # youtube-dl 라이브러리 사용

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -protocol_whitelist file,http,https,tcp,tls,crypto',
    'options': '-vn'
}

queue = []
current_player = None

# 곡이 끝나면 다음 곡을 재생하는 함수
def play_next(ctx):
    global current_player
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    
    if queue:
        current_player = queue.pop(0)
        voice_client.play(current_player, after=lambda e: play_next(ctx))

        # 곡 길이 가져오기
        duration_seconds = current_player.info['duration']
        minutes, seconds = divmod(duration_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"

        # 대기열 형식
        queue_info = '없음' if not queue else str(len(queue))

        # 재생한 사람 정보 추가
        played_by = ctx.message.author  # 재생한 사람의 이름

        # 테이블 형식으로 정보 정리
        embed = discord.Embed(
            title=f"🎵 {current_player.title}",
            color=discord.Color.blue()
        )
        embed.add_field(name="재생 시간", value=formatted_duration, inline=True)
        embed.add_field(name="영상", value=f"[링크]({current_player.url})", inline=True)
        embed.add_field(name="남은 대기열", value=queue_info, inline=True)
        embed.set_thumbnail(url=current_player.thumbnail)  # 이미지 크기를 작게 표시
        embed.set_author(name=f"{played_by.name}", icon_url=played_by.avatar.url)  # 작성자 정보 추가

        asyncio.run_coroutine_threadsafe(ctx.send(embed=embed), ctx.bot.loop)

class PlayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_player = None
        self.current_message = None

    @commands.command(name="재생")
    async def play(self, ctx, *, query: str):
        # 음성 채널에 접속되지 않은 경우 처리
        if not ctx.message.author.voice:
            embed = discord.Embed(title="❗재생 실패", description="먼저 음성 채널에 입장하세요.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        channel = ctx.message.author.voice.channel
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if not voice_client:
            # 음성 채널에 접속
            try:
                print(f"{ctx.author.name}님의 음성 채널에 접속 중...")
                voice_client = await channel.connect()
                print("음성 채널에 성공적으로 연결되었습니다.")
            except Exception as e:
                print(f"음성 채널 연결 중 오류 발생: {e}")
                embed = discord.Embed(title="❗오류", description="음성 채널 연결에 실패했어요.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return

        # 유튜브 검색 및 재생
        searched_by = ctx.message.author
        embed = discord.Embed(title="🔍 유튜브 검색 중...", color=discord.Color.green())
        embed.add_field(name=query, value="노래를 검색 중이에요.", inline=False)
        embed.set_author(name=f"{searched_by.name}", icon_url=searched_by.avatar.url)
        search_message = await ctx.send(embed=embed)

        async with ctx.typing():
            try:
                # 유튜브 URL 가져오기
                video_url = get_video_url(query)
                print(f"비디오 URL: {video_url}")

                # youtube-dl로 비디오 스트리밍을 위한 설정
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': 'downloads/%(id)s.%(ext)s',
                    'quiet': True,
                }

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=False)
                    url2 = info_dict['formats'][0]['url']

                # 음성을 재생
                voice_client.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options), after=lambda e: play_next(ctx))

                print(f"'{query}' 재생 시작")
            except asyncio.TimeoutError:
                print("유튜브 검색 시간이 초과되었습니다.")
                embed = discord.Embed(title="❗오류", description="유튜브 검색 시간을 초과했어요.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return
            except Exception as e:
                print(f"유튜브 검색 또는 재생 중 오류 발생: {e}")
                embed = discord.Embed(title="❗오류", description="곡을 검색하거나 재생하는데 실패했어요.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return
        
        await search_message.delete()

    @commands.command(name="현재노래")
    async def now_playing(self, ctx):
        if current_player:
            embed = discord.Embed(title="🎵 현재 재생 중", description=f"[{current_player.title}]({current_player.url})", color=discord.Color.blue())
            embed.set_image(url=current_player.thumbnail)  # 이미지 추가
            await ctx.send(embed=embed)
        else:
            await ctx.send("현재 재생 중인 음악이 없어요.")

async def setup(bot):
    await bot.add_cog(PlayCommand(bot))
