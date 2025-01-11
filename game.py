import pygame
import heapq
import time
from random import randint

# Grid size (2d array)
grid_size = 20
tile_size = 30
Screen_size = grid_size * tile_size
FPS = 10

# Colors rgb scale 0-->255 R G B
white = (255, 255, 255)  # walkable
black = (0, 0, 0)  # obstacle
red = (255, 0, 0)  # damage
yellow = (255, 255, 0)  # gold
green = (0, 255, 0)  # traversed (path)
blue = (0, 0, 255)  #  goals

# Cell types
walkable = 0
obstacle = 1
damage = 2
gold = 3  # Gold 
treasure = 4  # Treasures (goals)

hp = 100
gold_count = 10

# from the random library , use the randint function to randomly add obstacles ,gold and damage tiles to the grid
def make_grid():
    grid = [[walkable for _ in range(grid_size)] for _ in range(grid_size)]
    for row in range(grid_size):
        for col in range(grid_size):
            random_value = randint(1, 10)
            if random_value ==1:
                grid[row][col] = obstacle
            elif random_value in (2, 4,5, 9):
                grid[row][col] = damage
            elif random_value ==3:
                grid[row][col] = gold  
    
    # Set start and goal positions as walkable
    grid[0][0] = walkable
    grid[grid_size - 1][grid_size - 1] = walkable

    # Randomly place multiple treasure tiles aka goals
    treasurs_count = 5 # Number of treasure tiles
    for _ in range(treasurs_count):
        treasure_x, treasure_y = randint(0, grid_size - 1), randint(0, grid_size - 1)
        while grid[treasure_y][treasure_x] != walkable: #make sure that the tile type is walkable so the player can move to it
            treasure_x, treasure_y = randint(0, grid_size - 1), randint(0, grid_size - 1)
        grid[treasure_y][treasure_x] = treasure 
    
    return grid

# Heuristic function for A* (calculates the Manhattan distance between two points)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(grid, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    visited = {}
    g = {start: 0}#the cost of reaching each node from the start
    f = {start: heuristic(start, goal)}  #the f(x) of the A* algorithm ,heuristic + g(x)
    
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in visited:
                path.append(current)
                current = visited[current]
            path.reverse()
            return path
        
        for x_cordinates, y_cordinates in [(-1, 0), (1, 0), (0, -1), (0, 1)]:#the directions the player can move
            neighbor = (current[0] + x_cordinates, current[1] + y_cordinates)
            if 0 <= neighbor[0] < grid_size and 0 <= neighbor[1] < grid_size:
                     #  costs , walkable = 1 , damage = 10 , gold = 0.5, obstacle -->the algorithm will ignore obstacle tiles"""
                if grid[neighbor[1]][neighbor[0]] == obstacle:
                    continue
                tile_cost = 1
                if grid[neighbor[1]][neighbor[0]] == damage:
                    tile_cost = 10
                elif grid[neighbor[1]][neighbor[0]] == gold:
                    tile_cost = 0.5
                new_cost = g[current] + tile_cost
                if neighbor not in g or new_cost < g[neighbor]:
                    visited[neighbor] = current
                    g[neighbor] = new_cost
                    f[neighbor] = new_cost + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f[neighbor], neighbor))
    return []

# add colors to each tile in the grid based on its type
def color(screen, grid, traversed, goals):
    for row in range(grid_size):
        for col in range(grid_size):
            color = white
            if grid[row][col] == obstacle:
                color = black
            elif grid[row][col] == damage and (col, row) not in traversed:
                color = red
            elif grid[row][col] == gold and (col, row) not in traversed:
                color = yellow
            elif grid[row][col] == treasure:#goal
                color = blue
            elif (col, row) in traversed:#path
                color = green
             # this draws each tile at the specified coordinates
            pygame.draw.rect(screen, color, (col * tile_size, row * tile_size, tile_size, tile_size))
            pygame.draw.rect(screen, blue, (col * tile_size, row * tile_size, tile_size, tile_size), 1)
def main():
    global hp, gold_count
    pygame.init()# intialize the pygame library
    screen = pygame.display.set_mode((Screen_size, Screen_size))
    pygame.display.set_caption("Treasure Hunt")
    clock = pygame.time.Clock()# This creates a clock object, which is used to control the game's frame rate (how fast the game updates)

    grid = make_grid()
    start = (0, 0)
    
    # Find all goals (treasures)
    goals = [(col, row) for row in range(grid_size) for col in range(grid_size) if grid[row][col] == treasure]
    

    if not goals:
        print("No treasure found!")
        return

    i = 0 #Keeps track of which tile in the path we are currently on
    traversed = set()  #A set that tracks the tiles the player has traversed, which will be highlighted in green
    goals_reached = 0  # goal count (initialize to 0, not 5)
    total_treasures = len(goals)  # total number of treasures
    path = []

    for goal in goals:
        if i == 0:  
            current_path = a_star(grid, start, goal)
        else:  
            current_path = a_star(grid, path[-1], goal)
        
        # Add the path to the overall path
        path += current_path
        start = goal
        
        if not current_path:
            print("No path found to one of the treasures.")
            return
    
    running = True # A boolean flag to keep the game loop running until the user closes the window ,then the stats is printed  in the console
    i = 0
    # while the game is running (Game Loop) ,runs the game until running=false
    while running:
        screen.fill(white)
        color(screen, grid, traversed, goals)
        # If the user clicks the close button, the running flag is set to False, which will stop the game loop
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         running = False
        # update the stats
        if i < len(path):
            current = path[i]
            traversed.add(current)

            if grid[current[1]][current[0]] == damage:
                hp -= 10
            elif grid[current[1]][current[0]] == gold:
                gold_count += 10
            elif grid[current[1]][current[0]] == treasure:
                goals_reached += 1 
                grid[current[1]][current[0]] = walkable  

            if hp <= 0:
                print("Game Over! You lost all your health.")
                running = False # Stop the game loop

            i += 1 #move to next tile in the path 
            time.sleep(0.1) # If player's health reaches 0, stop the game
        
        # Display stats
        font = pygame.font.SysFont(None, 24)
        hp_text = font.render(f"HP: {hp}", True, blue)
        gold_text = font.render(f"Gold: {gold_count}", True, blue)
        goals_text = font.render(f"Goals Reached: {goals_reached}/{total_treasures}", True, blue)
        screen.blit(hp_text, (10, 10))
        screen.blit(gold_text, (10, 30))
        screen.blit(goals_text, (10, 50))

        pygame.display.flip()#to update screen
        clock.tick(FPS)

    if hp > 0: #if the player's health is greater than 0 , meqns that they reached all the treasures
        print(f"You reached all the treasures! Your stats are: {hp} HP and {gold_count} gold")

    pygame.quit()

main()
