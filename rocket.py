import asyncio
import curses
import time

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


def draw_stars(coroutines, canvas, timer):
    for coroutine in coroutines:
        coroutine.send(None)
        curses.curs_set(False)
    canvas.refresh()
    time.sleep(timer)


def draw(canvas):
    canvas.border()
    coordinates = scatter_stars()

    coroutines = [
        blink(canvas, *coordinate) for coordinate in coordinates
    ]
    draw_stars(coroutines, canvas, timer=0)
    while True:
        stars_to_flicker = randint(1, len(coroutines))
        flickering_stars = choices(coroutines, k=stars_to_flicker)
        draw_stars(flickering_stars, canvas, timer=0.1)


def scatter_stars():
    stars_ratio = 50

    screen = curses.initscr()
    rows, columns = screen.getmaxyx()
    stars_count = int(rows * columns / stars_ratio)

    coordinates = {(randint(2, rows - 2), randint(2, columns - 2))
                      for _ in range(stars_count)}

    for coordinate in coordinates:
        yield *coordinate, choice('+*.:')


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
