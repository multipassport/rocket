import curses
import os
import time

from random import randint, choice, choices

from async_tools import blink, animate_spaceship, pass_years, fill_orbit_with_garbage
from curses_tools import read_animation
from settings import coroutines


def cycle_coroutines(cycled_coroutines, canvas):
    for coroutine in cycled_coroutines.copy():
        try:
            coroutine.send(None)
        except StopIteration:
            cycled_coroutines.remove(coroutine)


def draw(canvas):
    tic_length = 0.1

    curses.curs_set(False)
    rows, columns = canvas.getmaxyx()
    star_coordinates = scatter_stars(rows, columns)
    rocket_frames_folder = './animations/rocket'
    garbage_frames_folder = './animations/garbage'

    starship_frames = [
        read_animation(os.path.join(rocket_frames_folder, filepath))
        for filepath in os.listdir(rocket_frames_folder)
    ]

    garbage_frames = [
        read_animation(os.path.join(garbage_frames_folder, filepath))
        for filepath in os.listdir(garbage_frames_folder)
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

    coroutines.append(fill_orbit_with_garbage(canvas, garbage_frames, columns))
    coroutines.append(pass_years(canvas))
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
