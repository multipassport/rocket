import asyncio
import curses
import time

from async_tools import blink, animate_spaceship, send_garbage_fly, sleep
from curses_tools import get_screen_size, draw_frame
from random import randint, choice, choices


garbage = []


async def fill_orbit_with_garbage(canvas, garbage_frames, columns):
    while True:
        garbage_frame = choice(garbage_frames)
        column = randint(1, columns)
        await sleep(randint(1, 10))
        coroutine = send_garbage_fly(canvas, column, garbage_frame)
        garbage.append(coroutine)


def cycle_coroutines(coroutines, canvas):
    for coroutine in coroutines.copy():
        try:
            coroutine.send(None)
        except StopIteration:
            coroutines.remove(coroutine)


def draw(canvas):
    curses.curs_set(False)
    rows, columns = get_screen_size()
    star_coordinates = scatter_stars(rows, columns)

    starship_frames = [
        read_animation('animations/rocket_frame_1.txt'),
        read_animation('animations/rocket_frame_2.txt'),
    ]

    garbage_frames = [
        read_animation('animations/garbage/trash_small.txt'),
        read_animation('animations/garbage/trash_large.txt'),
        read_animation('animations/garbage/trash_x1.txt'),
        read_animation('animations/garbage/duck.txt'),
        read_animation('animations/garbage/hubble.txt'),
        read_animation('animations/garbage/lamp.txt'),
    ]

    spaceships = [
        animate_spaceship(
            canvas, round(rows / 2),
            round(columns / 2),
            starship_frames,
        )]

    abc = fill_orbit_with_garbage(canvas, garbage_frames, columns)
    garbage.append(abc)
    coroutines = [
        blink(canvas, *coordinate) for coordinate in star_coordinates
    ]

    while True:
        canvas.border()
        stars_to_flicker = randint(1, len(coroutines))
        flickering_stars = choices(coroutines, k=stars_to_flicker)
        cycle_coroutines(flickering_stars, canvas)
        cycle_coroutines(spaceships, canvas)
        cycle_coroutines(garbage, canvas)
        canvas.refresh()
        time.sleep(0.1)


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
