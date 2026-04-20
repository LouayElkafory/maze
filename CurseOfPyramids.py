import pygame
import heapq

# --- Configuration ---
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 40
COLS, ROWS = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE

# Colors
TEXT_COLOR = (255, 255, 255)

# --- A* FUNCTIONS ---
def get_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def a_star(maze, start, goal):
    neighbors = [(0,1), (0,-1), (1,0), (-1,0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: get_distance(start, goal)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        close_set.add(current)

        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j

            if 0 <= neighbor[0] < COLS and 0 <= neighbor[1] < ROWS:
                if maze[neighbor[1]][neighbor[0]] == 1:
                    continue
            else:
                continue

            if neighbor in close_set:
                continue

            tentative_g = gscore[current] + 1

            if neighbor not in [i[1] for i in oheap] or tentative_g < gscore.get(neighbor, 0):
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g
                fscore[neighbor] = tentative_g + get_distance(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))

    return None


# --- INIT ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Curse of the Pyramids")
font = pygame.font.SysFont("Arial", 28)

# --- LOAD ASSETS ---
maze_img = pygame.image.load(r"C:\Users\zbookg4\Desktop\assets\maze.png").convert()
wall_tile = pygame.image.load(r"C:\Users\zbookg4\Desktop\assets\wall.png").convert() # صورة الطوب
floor_tile = pygame.image.load(r"C:\Users\zbookg4\Desktop\assets\floor.png").convert() # صورة الرملة
player_img = pygame.image.load(r"C:\Users\zbookg4\Desktop\assets\player.png").convert_alpha()
mummy_img = pygame.image.load(r"C:\Users\zbookg4\Desktop\assets\mummy.png").convert_alpha()
treasure_img = pygame.image.load(r"C:\Users\zbookg4\Desktop\assets\treasure.png").convert_alpha()

# --- RESIZE ---
maze_img = pygame.transform.scale(maze_img, (WIDTH, HEIGHT))
player_img = pygame.transform.smoothscale(player_img, (GRID_SIZE, GRID_SIZE))
mummy_img = pygame.transform.smoothscale(mummy_img, (GRID_SIZE, GRID_SIZE))
treasure_img = pygame.transform.smoothscale(treasure_img, (GRID_SIZE, GRID_SIZE))

# --- MAZE LOGIC (تقريب للصورة) ---
maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,1,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,1,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,1,0,1],
    [1,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,0,1,1,1,1,1,1,1],
    [1,0,1,0,0,0,1,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,0,1,0,1,0,1],
    [1,1,1,0,1,0,1,1,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,1,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# --- POSITIONS ---
def reset_game():
    return [1, 1], [13, 13], "PLAYING"

player_pos, mummy_pos, game_state = reset_game()
treasure_pos = [13, 13]

# --- GAME LOOP ---
clock = pygame.time.Clock()
running = True

mummy_timer = 0
MUMMY_DELAY = 3   

while running:
  
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c * GRID_SIZE, r * GRID_SIZE
            if maze[r][c] == 1:
                screen.blit(wall_tile, (x, y))
            else:
                screen.blit(floor_tile, (x, y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "PLAYING":
                new_pos = list(player_pos)

                if event.key == pygame.K_UP: new_pos[1] -= 1
                if event.key == pygame.K_DOWN: new_pos[1] += 1
                if event.key == pygame.K_LEFT: new_pos[0] -= 1
                if event.key == pygame.K_RIGHT: new_pos[0] += 1

                if 0 <= new_pos[0] < COLS and 0 <= new_pos[1] < ROWS:
                    if maze[new_pos[1]][new_pos[0]] == 0:
                        player_pos = new_pos

            elif event.key == pygame.K_SPACE:
                player_pos, mummy_pos, game_state = reset_game()

    # --- AI ---
    if game_state == "PLAYING":
        mummy_timer += 1

        if mummy_timer >= MUMMY_DELAY:
            path = a_star(maze, tuple(mummy_pos), tuple(player_pos))
            if path:
                mummy_pos = list(path[0])
            mummy_timer = 0

        if player_pos == mummy_pos:
            game_state = "LOST"
        elif player_pos == treasure_pos:
            game_state = "WON"

    # --- DRAW ---
    screen.blit(treasure_img, (treasure_pos[0]*GRID_SIZE, treasure_pos[1]*GRID_SIZE))
    screen.blit(player_img, (player_pos[0]*GRID_SIZE, player_pos[1]*GRID_SIZE))
    screen.blit(mummy_img, (mummy_pos[0]*GRID_SIZE, mummy_pos[1]*GRID_SIZE))

    # --- UI ---
    if game_state != "PLAYING":
        msg = "VICTORY!" if game_state == "WON" else "YOU DIED!"
        text = font.render(msg + " Press SPACE", True, TEXT_COLOR)
        rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        pygame.draw.rect(screen, (0,0,0), rect.inflate(20,10))
        screen.blit(text, rect)

    pygame.display.flip()
    clock.tick(10)

pygame.quit()