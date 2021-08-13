import asyncio
import curses

from curses_tools import draw_frame, read_controls, get_frame_size, get_screen_size
from itertools import cycle


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


async def animate_spaceship(canvas, row, column, frames, speed=1):
    current_row, current_column = row, column
    screen_height, screen_width = get_screen_size()

    canvas.nodelay(True)
    for frame in cycle(frames):
        ship_length, ship_width = get_frame_size(frame)

        draw_frame(canvas, current_row, current_column, frame)
        await asyncio.sleep(0)

        draw_frame(canvas, current_row, current_column, frame, negative=True)
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        current_row += rows_direction * speed
        current_column += columns_direction * speed

        if current_row < 1:
            current_row = 1
        if current_row > (max_row := screen_height - ship_length - 1):
            current_row = max_row

        if current_column < 1:
            current_column = 1
        if current_column > (max_width := screen_width - ship_width - 1):
            current_column = max_width


async def send_garbage_fly(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
