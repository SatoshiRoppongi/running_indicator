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
import shelve
import settings

# カレントディレクトリにあるmy_tokensをオープンする
oauth_info = shelve.open('my_tokens', writeback=True)

# アクセストークンの有効期限がきれていたら、リフレッシュトークンを使って
# 新たなアクセストークン・リフレッシュトークンを取得する
if oauth_info['expires_at'] < datetime.datetime.now().timestamp():
    authdata = {
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': oauth_info['refresh_token']
    }
    requestpost = requests.post(
        'https://www.strava.com/api/v3/oauth/token', data=authdata)
    response = requestpost.json()
    # 各種情報を更新する
    oauth_info['access_token'] = response['access_token']
    oauth_info['refresh_token'] = response['refresh_token']
    oauth_info['expires_at'] = response['expires_at']

strava_access_token = oauth_info['access_token']

oauth_info.close()

apiPath = "https://www.strava.com/api/v3/activities/"

headers = {'Authorization': 'Bearer {}'.format(strava_access_token)}

# todo:最新のアクティビティIDを取得できるように書き換える
activity_id = "2969365131"

# activityデータを取得する
activity_data = requests.get(apiPath + activity_id, headers=headers).json()

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

# todo:自動的にアップされた動画を読み込むように書き換える
file_path = "movie.mp4"

# 秒を分に変換する => m'ss に変換する


def change_time_format(time_string):
    time = float(time_string)  # must be sec
    m, s = divmod(time, 60)
    return str(int(m)) + "'" + str(int(s))


def annotate(clip, txt, text_color='red', fontsize=200, font='Xolonium-Bold', pos=(0.4, 0.4), relative=True):
    # Write a text at the bottom of the clip.
    txtclip = editor.TextClip(txt, fontsize=fontsize,
                              font=font, color=text_color)
    cvc = editor.CompositeVideoClip(
        [clip, txtclip.set_pos(pos, relative)])
    return cvc.set_duration(clip.duration)


video = VideoFileClip(file_path)
print("video.duration")
print(video.duration)
end_time = video.duration

# ラップタイム履歴
laptime_history = []

# ADJUSTMENT_END_TIME = 20  # 終了時間20秒の調整
# splits_metric[-1]['elapsed_time'] = splits_metric[-1]['elapsed_time'] - ADJUSTMENT_END_TIME

# 行間隔
LINE_SPACING = 60
total_time_list = np.cumsum([split_info['elapsed_time']
                             for split_info in splits_metric])
for i, split_info in enumerate(splits_metric):
    split_info['total_time'] = total_time_list[i]
    text_info = {'pos': (10, 10 + i * LINE_SPACING)}
    laptime_history.append(text_info)


pprint.pprint(splits_metric)

# todo: 以下定数は外だしにしたい
DISPLAY_TIME = 2  # 10秒間表示する
TIME_SPEED = 32  # 何倍速にするか。
FLASH_FREQ = 2  # 0.25  # 1秒間に何回点滅するか
interval = 1 / FLASH_FREQ  # 点滅間隔(1回点滅するのにかかる時間)
center_time_text = [((min(int(split_info['total_time']/TIME_SPEED), end_time), min(int(split_info['total_time']/TIME_SPEED) + DISPLAY_TIME, end_time)), change_time_format(str(split_info['elapsed_time'])))
                    for split_info in splits_metric]

for i, time_text in enumerate(center_time_text):
    laptime_history[i]['display_start'] = time_text[0][1]
    laptime_history[i]['display_end'] = center_time_text[-1][0][1]
    laptime_history[i]['time_text'] = time_text[1]

print('laptime_history')
print(laptime_history)

print(center_time_text)

center_time_text_flashing = []
for center_time_text_item in center_time_text:
    prev_time_text = (
        (center_time_text_item[0][0], center_time_text_item[0][0] + interval / 2), center_time_text_item[1])
    center_time_text_flashing.append(prev_time_text)
    t = 0
    while t < FLASH_FREQ * TIME_SPEED:
        time_text_flashing_part = (
            (prev_time_text[0][0] + interval, prev_time_text[0][1] + interval), prev_time_text[1])
        center_time_text_flashing.append(time_text_flashing_part)
        prev_time_text = copy.deepcopy(time_text_flashing_part)
        t = t + 1

center_time_text = center_time_text_flashing
print("center_time_text(点滅後)")
print(center_time_text)

# 中央ラップタイム表示の間は、空の表示をする必要がある
complemented_time_text = [((0, center_time_text[0][0][0]), ' ')]
complemented_time_text.append(center_time_text[0])
prev_time_text = center_time_text[0]
for time_text in center_time_text[1:]:
    complemented_time_text.append(
        ((prev_time_text[0][1], time_text[0][0]), ' '))
    complemented_time_text.append(time_text)
    # prev_time_text = time_text
    prev_time_text = copy.deepcopy(time_text)

# complemented_time_text_flashing = []
# for time_text_item in complemented_time_text:

# center_time_text.pop()
print("最終的な値")
print(complemented_time_text)
# shit code below
# complemented_time_text = complemented_time_text[:-6]
# print("後半の一部を除外")
# print(complemented_time_text)
annotated_center_laptime_clips = [annotate(video.subclip(min(from_t, end_time), min(to_t, end_time)), txt) for (
    from_t, to_t), txt in complemented_time_text]  # 動画と字幕を繋げる処理
video = editor.concatenate_videoclips(annotated_center_laptime_clips)

print("laptime_history")
print(laptime_history)
i = 0
for lap_text in laptime_history:
    i = i + 1
    print(i)
    lap = [((0, lap_text['display_start']), ' '),
           ((min(lap_text['display_start'], end_time), min(lap_text['display_end'], end_time)), lap_text['time_text'])]
    print('lap pos')
    print(lap)
    if i == 9:  # for debug
        break

    annotated_laptime_history_subclip = [annotate(video.subclip(
        min(from_t, end_time), min(to_t, end_time)), txt, pos=lap_text['pos'], relative=False, fontsize=60)
        for (from_t, to_t), txt in lap]
    video = editor.concatenate_videoclips(annotated_laptime_history_subclip)

final_clip = video
final_clip.write_videofile("movie_withSubtitle.mp4",
                           threads=4, audio=False, fps=5)
# final_clip.write_videofile("testVideo.mp4", fps=1)
