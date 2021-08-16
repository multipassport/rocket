import curses
import time

from random import randint, choice, choices

from async_tools import blink, animate_spaceship, pass_years, fill_orbit_with_garbage
from curses_tools import read_animation
from obstacles import show_obstacles
from settings import coroutines, obstacles


def cycle_coroutines(coroutines, canvas):
    for coroutine in coroutines.copy():
        try:
            coroutine.send(None)
        except StopIteration:
            coroutines.remove(coroutine)


def draw(canvas):
    tic_length = 0.1

    curses.curs_set(False)
    rows, columns = canvas.getmaxyx()
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

    spaceships = animate_spaceship(
        canvas,
        round(rows / 2),
        round(columns / 2),
        starship_frames,
    )

    stars = [
        blink(canvas, *coordinate) for coordinate in star_coordinates
    ]

    garbage = fill_orbit_with_garbage(canvas, garbage_frames, columns)
    coroutines.append(show_obstacles(canvas, obstacles))
    coroutines.append(pass_years(canvas))
    coroutines.append(garbage)
    coroutines.append(spaceships)
    coroutines.extend(stars)

    while True:
        canvas.border()

        stars_to_flicker = randint(1, len(stars))
        flickering_stars = choices(stars, k=stars_to_flicker)

        cycle_coroutines(flickering_stars, canvas)
        cycle_coroutines(coroutines, canvas)
        canvas.refresh()
        time.sleep(tic_length)


def scatter_stars(rows, columns):
    stars_ratio = 50
    stars_count = int(rows * columns / stars_ratio)

    coordinates = {(randint(2, rows - 2), randint(2, columns - 2))
                   for _ in range(stars_count)}

    for coordinate in coordinates:
        yield *coordinate, choice('+*.:')


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
