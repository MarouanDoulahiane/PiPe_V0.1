import requests
import json
from moviepy.editor import *
import random
import os
import subprocess
import youtube_dl
from urllib.parse import urlparse, parse_qs

# print youtube_dl path
print(youtube_dl.__file__)


TextClip.list('font')

# I wanna create a bot that will automatically fetch hot movies from the API and upload each one per hour and save them in a database to avoid duplicates and also to keep track of the movies that have been uploaded.
ffmpeg_path = '/usr/bin/ffmpeg'

os.environ["FFMPEG_BINARY"] = ffmpeg_path
os.environ["FFPROBE_BINARY"] = "/usr/bin/ffprobe"

urlMovies = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1"
headerMovies = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlMTBhNTg2Y2VlYzlhY2Q0NDNjYjM2NDIxYWFmNzk2OSIsInN1YiI6IjY2MjE0MjRmY2NkZTA0MDE4ODA1YzU1YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.yZDD6KFv3qFqYZGEq5yGHVPaN7WiSrq84ZY490qMoqk"
}
response = requests.get(urlMovies, headers=headerMovies)
moviesDB = response.json()

urlSpeech = "https://api.edenai.run/v2/audio/text_to_speech"

headersSpeech = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjY5MjNiNmUtY2I3YS00NmU2LWFiYjktMWEzOGFjMzk0MmUyIiwidHlwZSI6ImFwaV90b2tlbiJ9.0ysUt_KR5d0MGWOIe7pb1yCiXX-Bd-yZVURU4tBowFI"
}




def get_keywords(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlMTBhNTg2Y2VlYzlhY2Q0NDNjYjM2NDIxYWFmNzk2OSIsInN1YiI6IjY2MjE0MjRmY2NkZTA0MDE4ODA1YzU1YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.yZDD6KFv3qFqYZGEq5yGHVPaN7WiSrq84ZY490qMoqk"
    }
    response = requests.get(url, headers=headers)
    keywords = response.json()
    results = []
    for keyword in keywords['keywords']:
        results.append(keyword['name'])
    return results


from pytube import YouTube

def download_video(url, output_path):
    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        print(f"Downloading: {yt.title}")
        video.download('tmp', filename=output_path)

        print("Download completed successfully!")
    except Exception as e:
        print(f"Error downloading video: {e}")

def get_video_id(url):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    video_id = query["v"][0] if "v" in query else None
    return video_id


def get_movie_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?language=en-US"
    headers = {
        "accept": "application/json",
         "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlMTBhNTg2Y2VlYzlhY2Q0NDNjYjM2NDIxYWFmNzk2OSIsInN1YiI6IjY2MjE0MjRmY2NkZTA0MDE4ODA1YzU1YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.yZDD6KFv3qFqYZGEq5yGHVPaN7WiSrq84ZY490qMoqk"
    }
    response = requests.get(url, headers=headers)
    trailer = response.json()
    trailerResults = trailer['results'][0]['key']
    # if it's a video in youtube
    for video in trailer['results']:
        if video['site'] == 'YouTube' or video['site'] == 'youtube':
            return video['key']
    return trailerResults


# def download_video(videoId, output_path):
#     # Download the video
#     url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"

#     querystring = {"videoId":videoId}

#     headers = {
#         'X-RapidAPI-Key': '8f08f20011msh2cd369dec7a2039p1052fajsnba70a0b6e04d',
#         'X-RapidAPI-Host': 'youtube-media-downloader.p.rapidapi.com'
#     }

#     response = requests.get(url, headers=headers, params=querystring)
#     print(json.dumps(response.json(), indent=4))
#     try:
#         videoUrlDownload = response.json()['videos']['items'][0]['url']
#     except Exception as e:
#         print(e)
#         return
#     videoResponse = requests.get(videoUrlDownload)
#     with open(output_path, "wb") as f:
#         f.write(videoResponse.content)


def extract_video_clips_X(video_path, nb_clips, duration):
    video = VideoFileClip(video_path)
    clips = []
    for i in range(nb_clips):
        print(f"Extracting clip {i + 1}..., duration: {duration} seconds")
        while True:
            start_time = random.randint(0, int(video.duration - duration))
            end_time = start_time + duration
            clip = video.subclip(start_time, end_time)
            if clip.audio.max_volume() > 0:
                clips.append(clip)
                break
    return clips

def extract_video_clips(video_path, duration):
    # check if video exists
    if not os.path.exists(video_path):
        print("Video does not exist")
        return []
    video = VideoFileClip(video_path)
    clips = []
  
    while True:
        start_time = random.randint(0, int(video.duration - duration))
        end_time = start_time + duration
        clip = video.subclip(start_time, end_time)
        if clip.audio.max_volume() > 0:
            clips.append(clip)
            break
    return clips
    
from moviepy.video.fx.resize import resize

def create_video_from_clips(clips, output_path, audio_path, video_path=None, image_path=None):
    # Concatenate video clips and set audio
    if clips == []:
        return
    final_clip = concatenate_videoclips(clips)
    audio = AudioFileClip(audio_path)
    final_clip = final_clip.set_audio(audio)
    
    # Load the image
    image = ImageClip(image_path, duration=final_clip.duration)
    # Resize the image to match the video dimensions
    image = image.fx(resize, width=final_clip.size[0], height=final_clip.size[1])
    # Overlay image onto the video
    final_clip = CompositeVideoClip([image.set_duration(72), final_clip])
    
    # Write the final video file
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=4, fps=24, preset='ultrafast')






with open("movie_ids.txt", "r") as f:
    movie_ids = f.read().split("\n")

# LANCZOS

for movie in moviesDB['results']:
    # check if the movie id is in the movie_ids.txt file
    # try :
    if str(movie['id']) in movie_ids:
        continue
    movie_id = movie['id']
    movie_title = movie['title']
    movie_overview = movie['overview']
    movie_release_date = movie['release_date']
    movie_poster_path = movie['poster_path']
    movie_image = f"https://image.tmdb.org/t/p/original/{movie['backdrop_path']}"
    # download the image and save it as $(id).jpg
    image_response = requests.get(movie_image)
    with open(f"tmp/{movie_id}.jpg", "wb") as f:
        f.write(image_response.content)
    # save the movie id in the database
    # we will use a simple text file to store the movie ids
    # with open("movie_ids.txt", "a") as f:
    #     f.write(str(movie_id) + "\n")
    
    payload = {
        "response_as_dict": True,
        "attributes_as_list": False,
        "show_original_response": False,
        "rate": 0,
        "pitch": 0,
        "volume": 0,
        "sampling_rate": 0,
        "providers": "google",
        "language": "en",
        "text": f"{movie_title} is a movie that was released on {movie_release_date}. {movie_overview}",
        "option": "MALE"
    }   
    responseSpeech = requests.post(urlSpeech, headers=headersSpeech, data=json.dumps(payload))
    voiceover = responseSpeech.json()
    voiceover_url = voiceover['google']['audio_resource_url']
    voiceover_response = requests.get(voiceover_url)
    with open(f"tmp/{movie_id}.mp3", "wb") as f:
        f.write(voiceover_response.content)

    # download_video(get_movie_trailer(movie_id), f"tmp/{movie_id}.mp4")
    # command = ["youtube-dl", "-o", f"tmp/{movie_id}.mp4", f"https://www.youtube.com/watch?v={get_movie_trailer(movie_id)}", "-f", 'bestvideo[height<=480]+bestaudio/best[height<=480]', 
    # "--recode-video", "mp4"]
    # subprocess.Popen(command)

    # ydl = {
    #     'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
    #     'outtmpl': f"tmp/{movie_id}",
    #     'recode-video': 'mp4'
    # }
    # with youtube_dl.YoutubeDL(ydl) as ydl:
    #     ydl.download([f"https://www.youtube.com/watch?v={get_movie_trailer(movie_id)}"])
    
    download_video(f"https://www.youtube.com/watch?v={get_video_id(f'https://www.youtube.com/watch?v={get_movie_trailer(movie_id)}')}", f"{movie_id}.mp4")


    # we must wait for the video to be downloaded
    # we can check if the file exists
    


    imageFrames = extract_video_clips(f"tmp/{movie_id}.mp4", 10)
    create_video_from_clips(imageFrames, f"out/{movie_id}_out.mp4", f"tmp/{movie_id}.mp3", f"tmp/{movie_id}.mp4", "ads.jpg")

    commandYoutube_uploader = ["python", "youtube_uploader.py", "--verbose", "--file", f"out/{movie_id}_out.mp4", "--title", movie_title, "--description", movie_overview, "--category", "22", "--keywords", "movies", "--privacyStatus", "public"]
    # subprocess.Popen(commandYoutube_uploader)

    # print keywords
    print(get_keywords(movie_id))

    #  remove the tmp files
    try:
        os.remove(f"tmp/{movie_id}.mp3")
        os.remove(f"tmp/{movie_id}.jpg")
        os.remove(f"tmp/{movie_id}.mp4")
    except:
        pass
    # next step is to upload the video to youtube