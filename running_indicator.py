import requests
import pprint
from moviepy import editor
from moviepy.video.io.VideoFileClip import VideoFileClip
import polyline
import datetime

import matplotlib.pyplot as plt
import math
import numpy as np
import copy



apiPath = "https://www.strava.com/api/v3/activities/"

# todo:最新のアクティビティIDを取得できるように書き換える
activity_id = "2969365131"

# 外部ファイルからアクセストークンを読み込む
# with open('somedir/strava_access_token.txt') as f:
#    strava_access_token = f.read().strip()
# またはdotenvなどから

# todo:上記読み込んだアクセストークンに書き換える
strava_access_token = "xxxxxxxxxxx"
headers = {'Authorization': 'Bearer {}'.format(strava_access_token)}

# activityデータを取得する
activity_data = requests.get(apiPath + activity_id, headers = headers).json()

# activityのスプリット情報 (配列)
splits_metric = activity_data['splits_metric']

# 緯度経度情報
lat_lon_arr = polyline.decode(activity_data['map']['polyline'])

pprint.pprint(splits_metric)

print(len(lat_lon_arr))


# x = [point[0] for point in lat_lon_arr]
# y = [point[1] for point in lat_lon_arr]
# plt.plot(y,x)
# plt.show()

file_path = "movie.mp4"

# ラップの平均ペース表記を、m.xx => m'ss に変換する
def change_time_format(time_string):
    time = float(time_string)  # must be minuites
    second = time * 60
    m, s = divmod(second, 60)
    return str(int(m)) + "'" + str(int(s))


def annotate(clip, txt, text_color='red', fontsize=200, font='Xolonium-Bold'):
    # Write a text at the bottom of the clip.
    txtclip = editor.TextClip(txt,fontsize=fontsize, font=font, color=text_color)
    cvc = editor.CompositeVideoClip([clip, txtclip.set_pos(('center', 'center'))])
    return cvc.set_duration(clip.duration)

video = VideoFileClip(file_path)

total_time_list = np.cumsum([ split_info['elapsed_time'] for split_info in splits_metric])
for i, split_info in enumerate(splits_metric):
   split_info['total_time'] = total_time_list[i]

print(total_time_list)

# todo: 以下定数は外だしにしたい
DISPLAY_TIME = 4 # 4秒間表示する
TIME_SPEED = 6 # 何倍速にするか。
center_time_text = [((split_info['total_time']/TIME_SPEED, split_info['total_time']/TIME_SPEED + DISPLAY_TIME), change_time_format(str(split_info['average_speed']))) 
                         for split_info in splits_metric]

print(center_time_text)

complemented_time_text = [((0,center_time_text[0][0][0]), ' ')]
complemented_time_text.append(center_time_text[0])
prev_time_text = center_time_text[0]
for time_text in center_time_text:
    complemented_time_text.append(((prev_time_text[0][1], time_text[0][0]),' '))
    complemented_time_text.append(time_text)
    prev_time_text = copy.deepcopy(time_text)

# center_time_text.pop()
print(complemented_time_text)
annotated_clips = [annotate(video.subclip(from_t, to_t), txt) for (from_t, to_t), txt in complemented_time_text]#動画と字幕を繋げる処理
final_clip = editor.concatenate_videoclips(annotated_clips)
# final_clip.write_videofile("movie_withSubtitle.mp4")
final_clip.write_videofile("testVideo.mp4", fps=1)