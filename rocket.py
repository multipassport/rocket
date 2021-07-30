import curses
import time

from async_tools import blink, animate_spaceship
from curses_tools import get_screen_size
from random import randint, choice, choices


def cycle_coroutines(coroutines, canvas, timer):
    for coroutine in coroutines.copy():
        try:
            coroutine.send(None)
        except StopIteration:
            coroutines.remove(coroutine)
        curses.curs_set(False)

    canvas.refresh()
    time.sleep(timer)


def draw(canvas):
    rows, columns = get_screen_size()
    star_coordinates = scatter_stars(rows, columns)

    starship_frames = [
        read_animation('animations/rocket_frame_1.txt'),
        read_animation('animations/rocket_frame_2.txt'),
    ]
    spaceships = [
        animate_spaceship(
            canvas, round(rows / 2),
            round(columns / 2),
            starship_frames,
        )]

    coroutines = [
        blink(canvas, *coordinate) for coordinate in star_coordinates
    ]

    cycle_coroutines(coroutines, canvas, timer=0)

    while True:
        canvas.border()
        stars_to_flicker = randint(1, len(coroutines))
        flickering_stars = choices(coroutines, k=stars_to_flicker)
        cycle_coroutines(flickering_stars, canvas, timer=0.1)
        cycle_coroutines(spaceships, canvas, timer=0)


def scatter_stars(rows, columns):
    stars_ratio = 50

    stars_count = int(rows * columns / stars_ratio)

    coordinates = {(randint(2, rows - 2), randint(2, columns - 2))
                   for _ in range(stars_count)}

    for coordinate in coordinates:
        yield *coordinate, choice('+*.:')


def read_animation(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
