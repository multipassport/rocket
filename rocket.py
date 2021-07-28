import asyncio
import curses
import time


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    row, column = (5, 20)
    canvas.border()
    star_coroutine = blink(canvas, row, column, '*')
    while True:
        star_coroutine.send(None)
        curses.curs_set(False)
        canvas.refresh()
    time.sleep(5)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
