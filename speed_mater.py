import gizeh
import moviepy.editor as mpy

Pi = 3.141592
W, H = 128, 128
R = 64


def make_speed_mater():
    surface = gizeh.Surface(W, H)
    arc = gizeh.arc(r=R, a1=Pi, a2=2 * Pi, xy=(W / 2, H), fill=(1, 1, 1))
    print(gizeh.polar2cart(128, Pi))
    line = gizeh.polyline(
        points=[(W/2, H), (W/2, H) + (gizeh.polar2cart(R,  4.65))], stroke_width=4, stroke=(1, 0, 0), fill=(0, 1, 0))
    arc.draw(surface)
    line.draw(surface)
    surface.get_npimage()
    surface.write_to_png("my_drawing.png")


make_speed_mater()
