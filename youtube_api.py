import os
from dotenv import load_dotenv
import googleapiclient.discovery

# .env 파일에서 환경변수 로드
load_dotenv()

# 환경변수에서 유튜브 API 키를 가져옴
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# 유튜브 API 클라이언트 설정
def get_youtube_client():
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=YOUTUBE_API_KEY)
    return youtube

# 유튜브 검색 함수
def search_youtube(query):
    youtube = get_youtube_client()
    
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    
    response = request.execute()
    
    if response["items"]:
        video = response["items"][0]
        video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
        video_title = video["snippet"]["title"]
        video_thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
        
        return {
            "url": video_url,
            "title": video_title,
            "thumbnail": video_thumbnail
        }
    else:
        return None
