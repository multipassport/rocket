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
    coroutines = [blink(canvas, row, column + index) for index in range(5)]
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                curses.curs_set(False)
                time.sleep(0.2)
            except StopIteration:
                coroutines.remove(coroutine)
            if not coroutines:
                break
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
