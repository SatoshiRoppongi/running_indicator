import gizeh
import moviepy.editor as mpy
import numpy as np

# スピードメータのパラメータ
W, H = 128, 128
R = 64

# 赤道半径
R_EARTH = 6378137.0


def make_frame(t, speed_list):

    surface = gizeh.Surface(W, H)
    max_speed = max(speed_list)
    c = 2 * np.pi / max_speed  # 係数

    arc = gizeh.arc(r=R, a1=np.pi, a2=2 * np.pi, xy=(W / 2, H), fill=(1, 1, 1))
    arc.draw(surface)

    for speed in speed_list:
        line = gizeh.polyline(
            points=[(W/2, H), (W/2, H) + (gizeh.polar2cart(R, np.pi + c * speed))], stroke_width=4, stroke=(1, 0, 0), fill=(0, 1, 0))
        line.draw(surface)
    return surface.get_npimage()
    # return surface.write_to_png("my_drawing.png")

# 緯度経度から距離を求める
# https://qiita.com/chiyoyo/items/b10bd3864f3ce5c56291#球面三角法を利用したもの


def google_distance(latlon_from, latlon_to):
    # 度 -> ラジアン
    rad_latlon_from = (np.deg2rad(latlon_from[0]), np.deg2rad(latlon_from[1]))
    rad_latlon_to = (np.deg2rad(latlon_to[0]), np.deg2rad(latlon_to[1]))

    average_lat = (rad_latlon_from[0] - rad_latlon_to[0]) / 2
    average_lon = (rad_latlon_from[1] - rad_latlon_to[1]) / 2

    return R_EARTH * 2 * np.arcsin(np.sqrt(np.power(np.sin(average_lat), 2) + np.cos(rad_latlon_from[0]) * np.cos(rad_latlon_to[0]) * np.power(np.sin(average_lon), 2)))


# if __name__ == '__main__':
#     make_speed_mater()
