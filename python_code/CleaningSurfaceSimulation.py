import pygame
import numpy as np
from heapq import heappop, heappush

# Screen and grid constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 30, 30
CELL_WIDTH = WIDTH // COLS
CELL_HEIGHT = HEIGHT // ROWS

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)

# Initialize the grid
def initialize_grid(rows, cols):
    grid = np.zeros((rows, cols), dtype=int)
    grid[:5, :5] = 1  # Example clusters
    grid[-5:, -5:] = 1
    grid[10:15, 10:15] = 1
    return grid

# A* Algorithm
def a_star(start, goal, grid):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    rows, cols = grid.shape
    open_set = []
    heappush(open_set, (0, start))
    came_from = {start: None}
    g_score = {start: 0}
    f_score = {start: abs(goal[0] - start[0]) + abs(goal[1] - start[1])}

    while open_set:
        current = heappop(open_set)[1]
        if current == goal:
            return reconstruct_path(came_from, goal)

        for dr, dc in directions:
            neighbor = (current[0] + dr, current[1] + dc)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and grid[neighbor[0], neighbor[1]] != -1:
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + abs(goal[0] - neighbor[0]) + abs(goal[1] - neighbor[1])
                    if neighbor not in [i[1] for i in open_set]:
                        heappush(open_set, (f_score[neighbor], neighbor))
    return []

def reconstruct_path(came_from, end):
    path = []
    current = end
    while current:
        path.append(current)
        current = came_from[current]
    return path[::-1]

# Draw grid and robots
def draw_grid(screen, grid, robots, home):
    screen.fill(BLACK)
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if grid[row, col] == 0 else GREEN
            pygame.draw.rect(screen, color, (col * CELL_WIDTH, row * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT))

    # Highlight home position
    pygame.draw.rect(screen, CYAN, (home[1] * CELL_WIDTH, home[0] * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT))

    # Draw robots and their battery percentages
    font = pygame.font.Font(None, 24)
    for robot in robots:
        x, y = robot["position"]
        pygame.draw.circle(screen, robot["color"], (y * CELL_WIDTH + CELL_WIDTH // 2, x * CELL_HEIGHT + CELL_HEIGHT // 2), CELL_WIDTH // 3)
        # Display battery percentage
        battery_text = font.render(f"{robot['battery']}%", True, RED)
        screen.blit(battery_text, (y * CELL_WIDTH + CELL_WIDTH // 4, x * CELL_HEIGHT - CELL_HEIGHT // 2))

    pygame.display.flip()

# Main simulation
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    grid = initialize_grid(ROWS, COLS)
    home = (ROWS // 2, COLS // 2)  # Define the home position

    # Robot initialization
    robots = [
        {"position": list(home), "color": BLUE, "battery": 100, "state": "working", "target": None} for _ in range(4)
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for robot in robots:
            if robot["state"] == "working":
                if robot["battery"] < 20:
                    robot["state"] = "returning"
                else:
                    # Move to closest cluster of `1`s
                    if not robot["target"]:
                        targets = np.argwhere(grid == 1)
                        if len(targets) > 0:
                            distances = [abs(robot["position"][0] - t[0]) + abs(robot["position"][1] - t[1]) for t in targets]
                            robot["target"] = tuple(targets[np.argmin(distances)])
                        else:
                            robot["state"] = "idle"

                    if robot["target"]:
                        path = a_star(tuple(robot["position"]), robot["target"], grid)
                        if path:
                            robot["position"] = list(path[1]) if len(path) > 1 else list(path[0])
                            robot["battery"] -= 1
                            if tuple(robot["position"]) == robot["target"]:
                                grid[robot["target"][0], robot["target"][1]] = 0  # Clear the cell
                                robot["target"] = None

            elif robot["state"] == "returning":
                path = a_star(tuple(robot["position"]), home, grid)
                if path:
                    robot["position"] = list(path[1]) if len(path) > 1 else list(path[0])
                    robot["battery"] -= 1
                    if tuple(robot["position"]) == home:
                        robot["state"] = "recharging"

            elif robot["state"] == "recharging":
                robot["battery"] += 5  # Recharge rate
                if robot["battery"] >= 100:
                    robot["battery"] = 100
                    robot["state"] = "working"

            elif robot["state"] == "idle":
    # Move to the center (home) and remain there
                if not robot["target"]:
                    robot["target"] = home  # Set the center as the target

                path = a_star(tuple(robot["position"]), robot["target"], grid)
                if path:
                    robot["position"] = list(path[1]) if len(path) > 1 else list(path[0])
                if tuple(robot["position"]) == robot["target"]:
                    robot["target"] = None  # Clear the target once at the center




#############************************####################
    #         elif robot["state"] == "idle":
    # # Assign random resting positions across the grid
    #               if not robot["target"]:
    #     # Generate a random resting position within the grid
    #                 rest_x = np.random.randint(ROWS)
    #                 rest_y = np.random.randint(COLS)
    #                 robot["target"] = (rest_x, rest_y)

    #               path = a_star(tuple(robot["position"]), robot["target"], grid)
    #               if path:
    #                 robot["position"] = list(path[1]) if len(path) > 1 else list(path[0])
    #                 if tuple(robot["position"]) == robot["target"]:
    #                      robot["target"] = None  # Clear the target after reaching the resting spot


        draw_grid(screen, grid, robots, home)
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()
