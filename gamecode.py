import random
import time
from datetime import datetime
import sweeperlib

# Constants
TILE_SIZE = 40  # Tile size in pixels

# Global state dictionary
state = {
    "grid": [],
    "revealed": [],
    "flags": [],
    "width": 0,
    "height": 0,
    "mines": 0,
    "game_over": False,
    "start_time": None,
    "end_time": None,
    "stats": []
}

def initialize_game(width, height, mines):
    """Initialize the game state."""
    state["width"] = width
    state["height"] = height
    state["mines"] = mines
    state["grid"] = [[0 for _ in range(width)] for _ in range(height)]
    state["revealed"] = [[False for _ in range(width)] for _ in range(height)]
    state["flags"] = [[False for _ in range(width)] for _ in range(height)]
    state["game_over"] = False
    state["start_time"] = time.time()
    state["end_time"] = None

    # Place mines
    place_mines(width, height, mines)
    calculate_numbers()

def place_mines(width, height, mines):
    """Randomly place mines on the grid."""
    mine_positions = set()
    while len(mine_positions) < mines:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        mine_positions.add((x, y))

    for x, y in mine_positions:
        state["grid"][y][x] = "x"

def calculate_numbers():
    """Calculate the numbers for each tile based on surrounding mines."""
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for y in range(state["height"]):
        for x in range(state["width"]):
            if state["grid"][y][x] == "x":
                continue

            count = 0
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < state["width"] and 0 <= ny < state["height"] and state["grid"][ny][nx] == "x":
                    count += 1

            state["grid"][y][x] = count

def reveal_tile(x, y):
    """Reveal the tile at the given coordinates."""
    if state["revealed"][y][x] or state["flags"][y][x] or state["game_over"]:
        return

    state["revealed"][y][x] = True

    if state["grid"][y][x] == "x":
        state["game_over"] = True
        state["end_time"] = time.time()
        return

    if state["grid"][y][x] == 0:
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < state["width"] and 0 <= ny < state["height"]:
                reveal_tile(nx, ny)

def toggle_flag(x, y):
    """Toggle a flag on the tile at the given coordinates."""
    if state["revealed"][y][x] or state["game_over"]:
        return

    state["flags"][y][x] = not state["flags"][y][x]

def draw_handler():
    """Handler for drawing the game screen."""
    sweeperlib.clear_window()
    sweeperlib.draw_background()

    for y in range(state["height"]):
        for x in range(state["width"]):
            screen_x, screen_y = x * TILE_SIZE, y * TILE_SIZE
            if state["revealed"][y][x]:
                value = state["grid"][y][x]
                sweeperlib.prepare_sprite(value, screen_x, screen_y)
            elif state["flags"][y][x]:
                sweeperlib.prepare_sprite("f", screen_x, screen_y)
            else:
                sweeperlib.prepare_sprite(" ", screen_x, screen_y)

    sweeperlib.draw_sprites()

def mouse_handler(x, y, button, modifiers):
    """Handler for mouse clicks."""
    grid_x, grid_y = x // TILE_SIZE, y // TILE_SIZE

    if grid_x < 0 or grid_x >= state["width"] or grid_y < 0 or grid_y >= state["height"]:
        return

    if button == sweeperlib.MOUSE_LEFT:
        reveal_tile(grid_x, grid_y)
    elif button == sweeperlib.MOUSE_RIGHT:
        toggle_flag(grid_x, grid_y)

    if check_win():
        state["game_over"] = True
        state["end_time"] = time.time()

def check_win():
    """Check if the player has won the game."""
    for y in range(state["height"]):
        for x in range(state["width"]):
            if not state["revealed"][y][x] and state["grid"][y][x] != "x":
                return False

    return True

def save_statistics():
    """Save game statistics."""
    duration = state["end_time"] - state["start_time"] if state["end_time"] else 0
    outcome = "Win" if check_win() else "Lose"
    stats = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration": round(duration, 2),
        "outcome": outcome,
        "mines": state["mines"]
    }
    state["stats"].append(stats)

def main_menu():
    """Main menu for the game."""
    while True:
        print("\n--- Minestomper ---")
        print("1. New Game")
        print("2. View Statistics")
        print("3. Quit")

        choice = input("Enter your choice: ")
        if choice == "1":
            width = int(input("Enter field width: "))
            height = int(input("Enter field height: "))
            mines = int(input("Enter number of mines: "))

            initialize_game(width, height, mines)
            sweeperlib.create_window(width * TILE_SIZE, height * TILE_SIZE)
            sweeperlib.set_draw_handler(draw_handler)
            sweeperlib.set_mouse_handler(mouse_handler)
            sweeperlib.start()
            save_statistics()
        elif choice == "2":
            print("\n--- Game Statistics ---")
            for stat in state["stats"]:
                print(stat)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
