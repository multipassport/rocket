import asyncio
import curses
import random
import time


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


def draw(canvas):
    stars_count = 100
    canvas.border()

    coroutines = [blink(canvas, *scatter_stars()) for _ in range(stars_count)]
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                curses.curs_set(False)
            except StopIteration:
                coroutines.remove(coroutine)
            if not coroutines:
                break
        time.sleep(0.1)
        canvas.refresh()


def scatter_stars():
    screen = curses.initscr()
    rows, columns = screen.getmaxyx()
    row = random.randint(1, rows - 1)
    column = random.randint(1, columns - 1)
    symbol = random.choice('+*.:')
    return row, column, symbol


if __name__ == '__main__':

    curses.update_lines_cols()
    curses.wrapper(draw)
