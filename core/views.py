from rest_framework.views import APIView
from django.core.files.base import ContentFile
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from rest_framework.response import Response
from rest_framework import status
from .models import YouTubeCaption
from .serializer import YoutubeCaptionSerializer
from rest_framework.viewsets import ModelViewSet
from .pagination import YoutubePagination
import requests
import json
import yt_dlp
import boto3

class CreateCaptionView(APIView):
    def post(self, request):
        video_id = request.data.get('url')
        if not video_id:
            return Response({'error': "url not found"}, status=status.HTTP_400_BAD_REQUEST)

        available_caption = YouTubeCaption.objects.filter(url=video_id).first()
        if available_caption:
            serialized_data = YoutubeCaptionSerializer(available_caption)
            return Response(data=serialized_data.data, status=status.HTTP_200_OK)
        try:
            S3_BUCKET_NAME = "yonas-cap"
            S3_FILE_KEY = "coc.txt"  # Path in S3

            # Download `coc.txt` from S3
            def download_cookie_file():
                s3 = boto3.client("s3")
                local_path = "/tmp/coc.txt"  # Lambda can write only to /tmp

                try:
                    s3.download_file(S3_BUCKET_NAME, S3_FILE_KEY, local_path)
                    return local_path
                except Exception as e:
                    return None
            coc_path = download_cookie_file()
            if not coc_path:
                raise ValueError("can't find cookie")
            options = {
                "cookiefile": coc_path, 
                "writesubtitles": True,  
                "writeautomaticsub": True,  
                "skip_download": True,     
                "quiet": True
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(video_id, download=False)
                subtitles = info.get("subtitles") or {}
                subtitle_url = ""
                print(subtitles)
                writen_url = next(
                            (link['url'] for lang in subtitles 
                            for link in subtitles[lang] 
                            if link.get('name') == 'English - Default' and link.get('ext') == 'json3'),
                            None
                        )

                # next((links.url for links in  subtitles[next(iter(subtitles))] if links['name'] == 'English - Default' and links['ext'] =='json3'),None)
                if not writen_url:
                    auto_captions = info.get("automatic_captions") or {}

                if writen_url:
                    subtitle_url = writen_url
                elif "en" in auto_captions:
                    subtitle_url = auto_captions["en"][0]["url"]
                    print(subtitle_url)
                

                if not subtitle_url:
                    return Response({'error':'subtitle not found '},status = status.HTTP_400_BAD_REQUEST)
                
                response = requests.get(subtitle_url)
                
                if response.status_code == 200:
                    subtitle_data = response.json()
                    json_data = json.dumps(subtitle_data, indent=4, ensure_ascii=False)

                    caption_instance = YouTubeCaption(
                        url=video_id,
                        type='W' if writen_url else 'A'
                    )
                    caption_instance.caption.save(f"{video_id}.json", ContentFile(json_data))
                    caption_instance.save()

                    serialized_data = YoutubeCaptionSerializer(caption_instance)
                    return Response(data=serialized_data.data, status=status.HTTP_201_CREATED)
                else:
                    raise ValueError('subtitle not found')
        except Exception as e :
            print(str(e))
            return Response({'url':f'subtitle not Found {str(e)}'},status=status.HTTP_400_BAD_REQUEST)
        
    
class YouTubeVideosViewSet(ModelViewSet):
    queryset = YouTubeCaption.objects.all()
    serializer_class = YoutubeCaptionSerializer
    pagination_class = YoutubePagination
