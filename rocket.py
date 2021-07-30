import asyncio
import curses
import time

from curses_tools import draw_frame
from itertools import cycle
from random import randint, choice, choices


async def blink(canvas, row, column, symbol='*'):
    while True:
        for _ in range(20):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)

        for _ in range(3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)

        for _ in range(5):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)

        for _ in range(3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, row, column, frames):
    for frame in cycle(frames):
        draw_frame(canvas, row, column, frame)
        canvas.refresh()
        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)
        await asyncio.sleep(0)


def draw_stars(coroutines, canvas, timer):
    try:
        for coroutine in coroutines.copy():
            coroutine.send(None)
            curses.curs_set(False)
        canvas.refresh()
        time.sleep(timer)
    except StopIteration:
        coroutines.remove(coroutine)


def draw(canvas):
    rows, columns = get_screen_size()
    fires = [fire(canvas, rows - 2, round(columns / 2))]
    star_coordinates = scatter_stars(rows, columns)
    frames = ['a', 'b']
    spaceships = [animate_spaceship(canvas, 50, 20, frames)]

    coroutines = [
        blink(canvas, *coordinate) for coordinate in star_coordinates
    ]
    draw_stars(coroutines, canvas, timer=0)
    while True:
        canvas.border()
        stars_to_flicker = randint(1, len(coroutines))
        flickering_stars = choices(coroutines, k=stars_to_flicker)
        draw_stars(flickering_stars, canvas, timer=0.1)
        draw_stars(spaceships, canvas, timer=0)
        draw_stars(fires, canvas, timer=0)


def get_screen_size():
    screen = curses.initscr()
    return screen.getmaxyx()


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
