from youtube_search import YoutubeSearch
from youtube_dl import YoutubeDL

BASE_URL = "http://youtube.com"

# From discordpy/examples/basic_voice.py
YTDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': 'temp/%(extractor_key)s/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

FFMPEG_OPTIONS = {
    'options': '-vn'
}

# returns URL of first video match
def search_first(keywords):
    results = YoutubeSearch(keywords, max_results = 1)
    return BASE_URL + results[0]['url_suffix']

# get stream data
def get_stream_data(url):
    with YoutubeDL(YTDL_OPTS) as YTDL:
        result = YTDL.extract_info(url, download=False)

    if 'entries' in result:
        video = result['entries'][0]

    return video
