import discord
from discord.ext import commands

class InfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="정보")
    @commands.command(name="명령어")
    @commands.command(name="도움말")
    async def info(self, ctx):
        embed = discord.Embed(
            title="⭐ 춘식이 정보",
            description="춘식이는 유튜브 음악을 재생하는 디스코드 봇이에요.",
            color=discord.Color.green()
        )

        embed.set_thumbnail(url=ctx.bot.user.avatar.url)  # 봇 프로필 이미지 추가
        embed.add_field(name="\u200b", value="\u200b", inline=False)  # 공백 추가

        embed.add_field(name="📝 명령어", value="아래 명령어를 사용하여 음악을 재생하고 관리할 수 있어요!", inline=False)

        embed.add_field(name="▶️ **!재생 [유튜브 링크 또는 검색어]**", 
                        value="유튜브 링크로 음악을 재생하거나 검색 결과에서 자동 선택하여 재생해요.", inline=False)
        embed.add_field(name="⏹ **!정지**", 
                        value="재생을 중지하고 봇이 음성 채널에서 퇴장해요. 대기열에 있는 노래들도 전부 삭제돼요.", inline=False)
        embed.add_field(name="⏯ **!일시정지 / !재개 / !다음**", 
                        value="현재 재생 중인 음악을 일시 정지하거나 다시 재생하며, 다음 곡으로 넘길 수도 있어요.", inline=False)
        embed.add_field(name="🎵 **!현재노래**", 
                        value="현재 재생 중인 음악 정보를 확인할 수 있어요.", inline=False)
        embed.add_field(name="📜 **!대기열**", 
                        value="대기열에 있는 음악 목록을 표시해요.", inline=False)
        embed.add_field(name="❌ **!삭제 [대기열 번호]**", 
                        value="대기열에서 특정 번호의 음악을 삭제해요.", inline=False)
        embed.add_field(name="🗑️ **!대기열삭제**", 
                        value="대기열에 있는 모든 음악을 삭제해요.", inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)  # 공백 추가

        embed.add_field(name="ℹ️ 정보", value="춘식이에 대해 더 알고 싶다면 아래 링크를 확인해주세요!", inline=False)
        embed.add_field(name="📌 **깃허브 저장소**", 
                        value="[춘식이 GitHub](https://github.com/itleews/discord-bot)", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
     await bot.add_cog(InfoCommand(bot))