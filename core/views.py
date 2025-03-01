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
import os
import tempfile
import re


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
            proxy = f"http://sp4fyid8qe:ll9f7bOeAd8to_7XbV@gate.smartproxy.com:7000"

            options = {
                'proxy': proxy,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "skip_download": True,
           
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(video_id, download=False)
                subtitles = info.get("subtitles") or {}
                subtitle_url = ""
                writen_url = ""

                key_lists = list(subtitles.keys())
                pattern = r"en-[\w-]+"

                matches = [word for word in key_lists if re.match(pattern, word)]
                print(subtitles)
                if 'en' in subtitles:
                    writen_url = subtitles["en"][0]["url"]
                elif len(matches) != 0:
                    writen_url = subtitles[matches[0]][0]["url"]
                    subtitle_url = writen_url
                else:
                    auto_captions = info.get("automatic_captions") or {}
                    if "en" in auto_captions:
                        subtitle_url = auto_captions["en"][0]["url"]
                
                print(subtitle_url,writen_url)

                if not subtitle_url:
                    return Response({'error': 'subtitle not found 1'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    response = requests.get(subtitle_url)
                    if response.status_code == 200:
                        subtitle_data = response.json()
                        
                        json_data = json.dumps(
                            subtitle_data, indent=4, ensure_ascii=False)

                        caption_instance = YouTubeCaption(
                            url=video_id,
                            type='W' if writen_url else 'A'
                        )
                        caption_instance.caption.save(f"{video_id}.json", ContentFile(json_data))
                        caption_instance.save()
                        
                        serialized_data = YoutubeCaptionSerializer(
                            caption_instance)
                        return Response(data=serialized_data.data, status=status.HTTP_201_CREATED)
                except:
                    return Response({
                        "url":video_id,
                        "caption":subtitle_url,
                        "type":writen_url
                    },status = status.HTTP_200_OK )
           
        except Exception as e:
            return Response({'url': f'subtitle not Found {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
                   


class YouTubeVideosViewSet(ModelViewSet):
    queryset = YouTubeCaption.objects.all()
    serializer_class = YoutubeCaptionSerializer
    pagination_class = YoutubePagination