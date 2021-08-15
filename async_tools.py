import asyncio
import curses

from curses_tools import draw_frame, read_controls, get_frame_size, get_screen_size
from itertools import cycle
from physics import update_speed

from explosion import explode
from obstacles import Obstacle
from settings import garbage, obstacles, year


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
        try:
            obstacle = Obstacle(row, column, uid='shot')
            obstacles.append(obstacle)

            for object in obstacles[:-1]:
                if obstacle.has_collision(object.row, object.column, object.rows_size, object.columns_size):
                    return None

            canvas.addstr(round(row), round(column), symbol)
            await asyncio.sleep(0)
            canvas.addstr(round(row), round(column), ' ')
            row += rows_speed
            column += columns_speed
        finally:
            if obstacle:
                obstacles.remove(obstacle)


async def animate_spaceship(canvas, row, column, frames, row_speed=0, column_speed=0):
    current_row, current_column = row, column
    screen_height, screen_width = get_screen_size()

    canvas.nodelay(True)
    for frame in cycle(frames):

        try:
            ship_length, ship_width = get_frame_size(frame)
            obstacle = Obstacle(current_row, current_column, ship_width, ship_length)
            obstacles.append(obstacle)

            for object in obstacles[:-1]:
                if obstacle.has_collision(object.row, object.column, object.rows_size, object.columns_size):
                    await show_game_over_caption(canvas)

            current_row, current_column, row_speed, column_speed = move_ship(
                canvas, frame, row_speed, column_speed, current_row, current_column
            )
            draw_frame(canvas, current_row, current_column, frame)
            await asyncio.sleep(0)

            draw_frame(canvas, current_row, current_column, frame, negative=True)
            current_row, current_column, row_speed, column_speed = move_ship(
                canvas, frame, row_speed, column_speed, current_row, current_column
            )
        finally:
            obstacles.remove(obstacle)


async def send_garbage_fly(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    row_size, column_size = get_frame_size(garbage_frame)

    while row < rows_number:
        try:
            obstacle = Obstacle(row, column, row_size, column_size)
            obstacles.append(obstacle)

            # shot_obstacle = Obstacle(uid='shot')
            for object in obstacles[:-1]:
                if obstacle.has_collision(object.row, object.column, object.rows_size, object.columns_size):
                    await explode(canvas, object.row, object.column)
                    return None

            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
        finally:
            obstacles.remove(obstacle)


def read_animation(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()


async def show_game_over_caption(canvas):
    rows_number, columns_number = canvas.getmaxyx()

    caption = read_animation('animations/game_over.txt')
    while True:
        draw_frame(canvas, rows_number / 3, columns_number / 3, caption)
        await asyncio.sleep(0)


async def pass_years(canvas, year):
    rows_number, columns_number = canvas.getmaxyx()

    while True:
        draw_frame(canvas, rows_number - 1, columns_number - 10, str(year))
        year += 1
        await asyncio.sleep(0)


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


def move_ship(canvas, frame, row_speed, column_speed, current_row, current_column):
    rows_direction, columns_direction, space_pressed = read_controls(canvas)
    row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)
    screen_height, screen_width = canvas.getmaxyx()
    ship_length, ship_width = get_frame_size(frame)

    if space_pressed:
        shot_column = current_column + ship_width / 2
        shot = fire(canvas, current_row, shot_column)
        garbage.append(shot)
    current_row += row_speed
    current_column += column_speed

    if current_row < 1:
        current_row = 1
    if current_row > (max_row := screen_height - ship_length - 1):
        current_row = max_row

    if current_column < 1:
        current_column = 1
    if current_column > (max_width := screen_width - ship_width - 1):
        current_column = max_width
    return current_row, current_column, row_speed, column_speed

