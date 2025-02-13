# 디스코드 노래봇

디스코드 서버에서 음악을 재생할 수 있는 봇입니다. YouTube, 로컬 파일 등을 재생하며, 다양한 음악 명령어를 제공합니다.

---

## 기능

- **!재생 [URL 또는 검색어]** - 음악을 재생합니다.
- **!정지** - 음악을 멈추고 봇이 음성 채널에서 퇴장합니다.
- **!대기열** - 현재 대기열을 표시합니다.
- **!스킵** - 현재 재생 중인 노래를 스킵합니다.
- **!삭제 [번호]** - 대기열에서 특정 번호의 노래를 삭제합니다.
- **!명령어** - 사용 가능한 명령어 리스트를 표시합니다.

---

## 설치

1. **필수 사항**  
   - Python 3.8 이상 3.12 이하
   - `discord.py` 및 `yt-dlp`, `PyNaCl` 라이브러리 설치
     ```
     pip install discord.py
     pip install yt-dlp
     pip install PyNaCl
     ```
   - [ffmpeg 설치](https://ffmpeg.org/download.html)

2. **봇 토근 설정**
   - bot_token.py 파일을 생성하고, token 변수에 디스코드 봇 토큰 넣기
   ```
   token = 'YOUR_BOT_TOKEN'
   ```