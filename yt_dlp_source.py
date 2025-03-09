import yt_dlp
import discord

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")
        self.thumbnail = data.get("thumbnail")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioquality': 1,
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,  # Only download single video, not playlists
            'quiet': True,
            'logtostderr': False,
        }
        if stream:
            ydl_opts['noplaylist'] = True
            ydl_opts['format'] = 'bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Extract the best audio stream
            url2 = info['formats'][0]['url'] if stream else info['url']
            return cls(discord.FFmpegPCMAudio(url2), data=info)
