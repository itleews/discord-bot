import discord
from discord.ext import commands
import os
import asyncio
from bot_token import token

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

#명령어 폴더 내 모든 cog 파일 불러오기
async def load_extensions():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py") and filename != "__init__.py" and filename != "queue_manager.py":  # __init__.py 및 queue_manager.py 제외
            await bot.load_extension(f"commands.{filename[:-3]}")  # 확장 불러오기

@bot.event
async def on_ready():
     print(f"{bot.user} 봇이 준비됨! 로드된 명령어: {[cmd.name for cmd in bot.commands]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)
    
# 이미 실행 중인 이벤트 루프가 있으면 create_task 사용
try:
    asyncio.run(main())
except RuntimeError:
    loop = asyncio.get_event_loop()
    loop.create_task(main())