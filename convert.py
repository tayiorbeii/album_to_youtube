import glob
import moviepy.editor as mpy
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import os.path
import youtube_upload.auth
import youtube_upload.main as ytup
# import scipy
from pydub import AudioSegment



# TODO: Convert this from a class to a simple dict
class MusicVid(object):
    def __init__(self, title, description, category, tags, privacy, location, file):
        self.title = title
        self.description = description
        self.category = category
        self.tags = tags
        self.privacy = privacy
        self.location = location
        self.file = file

##############

# This all works:

# # Set location of ffmpeg
AudioSegment.ffmpeg = "/usr/local/bin/ffmpeg"
#
# Prepare the video info
video_title = ""
video_description = ""
start_time = 0

# # Search for all mp3 files in directory
list_of_songs = glob.glob("*.mp3")
for mp3_file in list_of_songs:

    m, s = divmod(start_time, 60)
    h, m = divmod(m, 60)
    time = "%d:%02d:%02d" % (h, m, s)

    length = MP3(mp3_file).info.length

    audio = ID3(mp3_file)
    video_title = audio['TPE1'].text[0] + " - " + audio['TALB'].text[0]
    track_info = audio['TRCK'].text[0] + " - " + audio['TIT2'].text[0]

    video_description += track_info + " (" + time + ")\n"
    start_time += length

print video_description



playlist_songs = [AudioSegment.from_mp3(mp3_file) for mp3_file in list_of_songs]

# Combine all songs into one file
combined = AudioSegment.empty()
for song in playlist_songs:
    combined += song

# Export the mp3 as merge.mp3
combined.export("merge.mp3", format="mp3", bitrate="320k")

# Prepare the video's audio track to be merge.mp3
audio_track = mpy.AudioFileClip('merge.mp3')


# Look for an image file to use in the video
artwork = sorted(glob.glob("*.jpg"))
if len(artwork) > 0:
    # Choose the first image file found in the directory
    picture = mpy.ImageClip(str(artwork[0]))
    # Center the image on black background
    picture = picture.on_color(size=(1280, 720), color=(0, 0, 0))
else:
    # Create plain black video
    picture = mpy.ColorClip(size=(1280, 720), col=(0, 0, 0))

picture = picture.set_audio(audio_track)
picture = picture.set_duration(audio_track.duration)

picture.write_videofile("output.mp4", fps=24, codec='mpeg4')


##############
# This all works:

mvid = MusicVid(video_title, video_description, "Music", "", "unlisted", "=", 'output.mp4')
home = os.path.expanduser("~")
client_secrets = os.path.join(home, '.client_secrets.json')
credentials = os.path.join(home, ".youtube-upload-credentials.json")
youtube = youtube_upload.auth.get_resource(client_secrets, credentials)
ytup.upload_video(youtube, mvid, "output.mp4", 1, 1)