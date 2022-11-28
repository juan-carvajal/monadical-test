def check_grid(grid: list[list[str | None]], target: int, value: str, x: int, y: int):
    dirs = [
        [(1, 0), (-1, 0)],
        [(0, 1), (0, -1)],
        [(1, 1), (-1, -1)],
        [(-1, 1), (1, -1)]
    ]

    max_count = 1
    for dir in dirs:
        temp = check_dir(grid, target, value, x, y, dir[0][0], dir[0][1], 1) + check_dir(
            grid, target, value, x, y, dir[1][0], dir[1][1], 1) - 1
        if temp > max_count:
            max_count = temp

    return max_count >= target, max_count


def check_dir(grid: list[list[str | None]], target: int, value: str, x: int, y: int, dx: int, dy: int, count: int):
    if(count >= target):
        return count

    next_x = x + dx
    next_y = y + dy
    if (next_y < 0 or next_x < 0 or next_x >= len(grid) or next_y >= len(grid[0])):
        return count

    if (grid[next_x][next_y] != value):
        return count

    return check_dir(grid, target, value, next_x, next_y, dx, dy, count + 1)
