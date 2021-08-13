import asyncio
import curses
import time

from async_tools import blink, animate_spaceship, send_garbage_fly, sleep
from random import randint, choice, choices
from curses_tools import draw_frame, read_controls, get_frame_size, get_screen_size
from itertools import cycle
from physics import update_speed

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


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


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


async def animate_spaceship(canvas, row, column, frames, row_speed=0, column_speed=0):
    current_row, current_column = row, column
    screen_height, screen_width = get_screen_size()

    canvas.nodelay(True)
    for frame in cycle(frames):
        ship_length, ship_width = get_frame_size(frame)
        current_row, current_column, row_speed, column_speed = move_ship(
            canvas, frame, row_speed, column_speed, current_row, current_column
        )
        draw_frame(canvas, current_row, current_column, frame)
        await asyncio.sleep(0)

        draw_frame(canvas, current_row, current_column, frame, negative=True)
        current_row, current_column, row_speed, column_speed = move_ship(
            canvas, frame, row_speed, column_speed, current_row, current_column
        )


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


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


def move_ship(canvas, frame, row_speed, column_speed, current_row, current_column):
    rows_direction, columns_direction, space_pressed = read_controls(canvas)
    row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)
    screen_height, screen_width = canvas.getmaxyx()
    ship_length, ship_width = get_frame_size(frame)
    current_row += row_speed
    current_column += column_speed
    if space_pressed:
        shot_column = current_column + ship_width / 2
        shot = fire(canvas, current_row, shot_column)
        garbage.append(shot)

    if current_row < 1:
        current_row = 1
    if current_row > (max_row := screen_height - ship_length - 1):
        current_row = max_row

    if current_column < 1:
        current_column = 1
    if current_column > (max_width := screen_width - ship_width - 1):
        current_column = max_width
    return current_row, current_column, row_speed, column_speed


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)