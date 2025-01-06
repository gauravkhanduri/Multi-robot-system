import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Screen and Grid Configuration
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
GRID_ROWS, GRID_COLUMNS = 30, 30
CELL_SIZE = SCREEN_WIDTH // GRID_COLUMNS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Rust target color
ORANGE = (255, 165, 0)  # Detected rust color
RED = (255, 0, 0)
BLUE = (0, 0, 255)  # Visited trail
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GREY = (200, 200, 200)

# Initialize Grid
def initialize_grid(rows, columns):
    grid = np.zeros((rows, columns), dtype=int)
    cluster_size = 5
    grid[:cluster_size, :cluster_size] = 1  # Top-left corner
    grid[:cluster_size, -cluster_size:] = 1  # Top-right corner
    grid[-cluster_size:, :cluster_size] = 1  # Bottom-left corner
    grid[-cluster_size:, -cluster_size:] = 1  # Bottom-right corner
    return grid

# Draw Grid
def draw_grid(screen, grid, pheromone_grid):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLUMNS):
            x, y = col * CELL_SIZE, row * CELL_SIZE
            color = GREY if pheromone_grid[row, col] > 0 else WHITE
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE), 0)
            if grid[row, col] == 1:  # Rust target not yet detected
                pygame.draw.circle(screen, GREEN, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), CELL_SIZE // 4)
            elif grid[row, col] == 2:  # Rust target detected
                pygame.draw.circle(screen, ORANGE, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), CELL_SIZE // 4)
            elif pheromone_grid[row, col] > 0:  # Pheromone trail
                pygame.draw.circle(screen, BLUE, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), CELL_SIZE // 6)

    # Draw Grid Lines
    for row in range(GRID_ROWS + 1):
        pygame.draw.line(screen, BLACK, (0, row * CELL_SIZE), (SCREEN_WIDTH, row * CELL_SIZE))
    for col in range(GRID_COLUMNS + 1):
        pygame.draw.line(screen, BLACK, (col * CELL_SIZE, 0), (col * CELL_SIZE, SCREEN_HEIGHT))

# Lévy walk calculation with quadrant restriction
def levy_walk_position(current_pos, quadrant, mu=2, max_step=10):
    """
    Compute the next position for a Lévy walk within a defined quadrant.
    :param current_pos: Current position (row, col)
    :param quadrant: Tuple defining the quadrant boundaries (r_min, r_max, c_min, c_max)
    :param mu: Lévy exponent (default 2)
    :param max_step: Maximum step length
    :return: New position (row, col)
    """
    r_min, r_max, c_min, c_max = quadrant
    step_length = int(np.random.pareto(mu) + 1)
    step_length = min(step_length, max_step)
    angle = np.random.uniform(0, 2 * np.pi)
    delta_r = int(step_length * np.sin(angle))
    delta_c = int(step_length * np.cos(angle))
    new_r = max(r_min, min(r_max - 1, current_pos[0] + delta_r))
    new_c = max(c_min, min(c_max - 1, current_pos[1] + delta_c))
    return new_r, new_c

# Move Agent with Lévy Walk in a quadrant
def move_agent_levy(agent, grid, pheromone_grid):
    if not agent["done"]:
        new_pos = levy_walk_position(agent["position"], agent["range"])
        agent["position"] = list(new_pos)
        pheromone_grid[new_pos[0], new_pos[1]] += 1
        if grid[new_pos[0], new_pos[1]] == 1:  # Detect rust
            grid[new_pos[0], new_pos[1]] = 2  # Mark as detected (change to ORANGE)
        if not np.any(grid == 1):  # Check if all rust locations are detected
            agent["done"] = True

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Lévy Walk Multi-Agent Search with Rust Detection")
    clock = pygame.time.Clock()

    grid = initialize_grid(GRID_ROWS, GRID_COLUMNS)
    pheromone_grid = np.zeros((GRID_ROWS, GRID_COLUMNS), dtype=int)

    mid_row, mid_col = GRID_ROWS // 2, GRID_COLUMNS // 2
    quadrants = [
        {"range": (0, mid_row, 0, mid_col), "color": RED},
        {"range": (0, mid_row, mid_col, GRID_COLUMNS), "color": BLUE},
        {"range": (mid_row, GRID_ROWS, 0, mid_col), "color": YELLOW},
        {"range": (mid_row, GRID_ROWS, mid_col, GRID_COLUMNS), "color": CYAN},
    ]

    agents = [
        {"position": [mid_row // 2, mid_col // 2], "range": quadrants[0]["range"], "color": quadrants[0]["color"], "done": False},
        {"position": [mid_row // 2, mid_col + mid_col // 2], "range": quadrants[1]["range"], "color": quadrants[1]["color"], "done": False},
        {"position": [mid_row + mid_row // 2, mid_col // 2], "range": quadrants[2]["range"], "color": quadrants[2]["color"], "done": False},
        {"position": [mid_row + mid_row // 2, mid_col + mid_col // 2], "range": quadrants[3]["range"], "color": quadrants[3]["color"], "done": False},
    ]

    master_agent = {"position": [mid_row, mid_col], "color": WHITE}
    running = True

    while running:
        screen.fill(BLACK)
        draw_grid(screen, grid, pheromone_grid)

        # Draw agents and move them
        for agent in agents:
            if not agent["done"]:
                move_agent_levy(agent, grid, pheromone_grid)
            else:
                # Return to master agent
                agent["position"][0] += np.sign(master_agent["position"][0] - agent["position"][0])
                agent["position"][1] += np.sign(master_agent["position"][1] - agent["position"][1])

            pygame.draw.circle(
                screen,
                agent["color"],
                (agent["position"][1] * CELL_SIZE + CELL_SIZE // 2, agent["position"][0] * CELL_SIZE + CELL_SIZE // 2),
                CELL_SIZE // 3,
            )

        # Draw master agent
        pygame.draw.circle(
            screen,
            master_agent["color"],
            (master_agent["position"][1] * CELL_SIZE + CELL_SIZE // 2, master_agent["position"][0] * CELL_SIZE + CELL_SIZE // 2),
            CELL_SIZE // 3,
        )

        # Check if all agents are done and at home
        if all(agent["done"] and agent["position"] == master_agent["position"] for agent in agents):
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QcommunityUIT:
                running = False

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()
