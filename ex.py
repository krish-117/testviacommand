import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Astronaut in a Spaceship")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Font
font = pygame.font.SysFont(None, 36)

# Load astronaut image
astronaut_img = pygame.image.load("astronautee.png")
astronaut_img = pygame.transform.scale(astronaut_img, (50, 70))

# Spaceship environment
spaceship_width = SCREEN_WIDTH
spaceship_height = SCREEN_HEIGHT // 2
spaceship_surface = pygame.Rect(0, SCREEN_HEIGHT // 2, spaceship_width, spaceship_height)

# Player (Astronaut) variables
astronaut_x = 100
astronaut_y = spaceship_surface.y + spaceship_surface.height - 70  # Bottom of spaceship
base_speed = 10  # Increased speed
astronaut_speed_x = 0
astronaut_speed_y = 0
friction = 0.9  # Friction factor to slow movement
acceleration = 1.5  # Acceleration factor
max_speed = 10  # Max speed to prevent too fast movement

weight = 70  # Weight in kg (starting value)
microgravity_effect = 0.01  # Weight loss factor per frame due to microgravity
health_factor = 100  # Health factor

# Health depletion thresholds
critical_oxygen_threshold = 40  # Oxygen below this level decreases health rapidly
critical_power_threshold = 30  # Power below this level decreases health
low_weight_threshold = 50  # Weight below this level decreases health due to malnutrition

# System variables (Oxygen, Power, etc.)
oxygen_level = 100  # Starting oxygen level
power_level = 100  # Starting power level
system_failure = False
system_failure_timer = 0
failure_threshold = 300  # Time until system fails completely (reduced for more urgency)

# Constants for resource depletion (starting values)
oxygen_depletion_rate = 0.075  # Constant depletion rate for oxygen
power_depletion_rate = 0.05   # Constant depletion rate for power

# Random system failure positions (random part of spaceship to repair)
system_x = random.randint(50, SCREEN_WIDTH - 100)
system_y = random.randint(spaceship_surface.y + 50, spaceship_surface.y + spaceship_surface.height - 100)

# Despawn time: 7 seconds (in milliseconds)
despawn_time_ms = 7000
base_respawn_time_ms = 13000  # Base respawn time of 13 seconds (in milliseconds)

# Tool (to fix systems) variables
tools = []
num_tools = 3  # Number of tools to collect
for _ in range(num_tools):
    tool_x = random.randint(100, SCREEN_WIDTH - 100)
    tool_y = random.randint(spaceship_surface.y + 50, spaceship_surface.y + spaceship_surface.height - 100)
    tools.append([tool_x, tool_y, False])  # (x, y, collected)

# Food variables
food_x = random.randint(100, SCREEN_WIDTH - 100)
food_y = random.randint(spaceship_surface.y + 50, spaceship_surface.y + spaceship_surface.height - 100)
food_collected = False
food_spawn_time = pygame.time.get_ticks()  # Record the time when food spawns
food_despawn_time = 0  # To track when food despawns
food_respawn_time_ms = base_respawn_time_ms  # Dynamic respawn time based on difficulty

# Power Kit variables
power_kit_x = random.randint(100, SCREEN_WIDTH - 100)
power_kit_y = random.randint(spaceship_surface.y + 50, spaceship_surface.y + spaceship_surface.height - 100)
power_kit_collected = False
power_kit_spawn_time = pygame.time.get_ticks()  # Record the time when power kit spawns
power_kit_despawn_time = 0  # To track when power kit despawns
power_kit_respawn_time_ms = base_respawn_time_ms  # Dynamic respawn time

# Oxygen Tank variables
oxygen_tank_x = random.randint(100, SCREEN_WIDTH - 100)
oxygen_tank_y = random.randint(spaceship_surface.y + 50, spaceship_surface.y + spaceship_surface.height - 100)
oxygen_tank_collected = False
oxygen_tank_spawn_time = pygame.time.get_ticks()  # Record the time when oxygen tank spawns
oxygen_tank_despawn_time = 0  # To track when oxygen tank despawns
oxygen_tank_respawn_time_ms = base_respawn_time_ms  # Dynamic respawn time

# Failure handling variables
failure_timer = 0
failure_interval = random.randint(300, 800)  # Increased failure frequency
failure_penalty_timer = 0
penalty_threshold = 200  # Time after which penalty is applied (reduced)

# Game Over countdown timer
game_over_timer = 200  # Countdown timer when critical levels are low

# Difficulty management
difficulty_timer = 0  # Track how long the player has survived
difficulty_level = 1  # Start at level 1
difficulty_increase_interval = 1000  # Increase difficulty every 1000 frames
system_failure_rate_increase = 0.05  # Rate at which system failures become more frequent

# Clock
clock = pygame.time.Clock()

# Game Over flag
game_over = False

def draw_astronaut(x, y):
    """Draw the astronaut on the screen."""
    screen.blit(astronaut_img, (x, y))

def draw_spaceship():
    """Draw the spaceship interior."""
    pygame.draw.rect(screen, BLUE, spaceship_surface, 2)  # Outline of spaceship

def draw_system_failure(x, y):
    """Draw a system failure spot (where astronaut needs to go)."""
    pygame.draw.rect(screen, RED, [x, y, 60, 60])  # System failure is a red square

def draw_tool(x, y):
    """Draw the tool that the astronaut needs to collect to fix systems."""
    pygame.draw.rect(screen, GREEN, [x, y, 30, 30])  # Tool is a green square

def draw_food(x, y):
    """Draw the food that the astronaut can collect."""
    pygame.draw.rect(screen, YELLOW, [x, y, 20, 20])  # Food is a yellow square

def draw_power_kit(x, y):
    """Draw the power kit that the astronaut can collect to restore power."""
    pygame.draw.rect(screen, (0, 128, 255), [x, y, 25, 25])  # Power kit is a blue square

def draw_oxygen_tank(x, y):
    """Draw the oxygen tank that the astronaut can collect to restore oxygen."""
    pygame.draw.rect(screen, CYAN, [x, y, 25, 25])  # Oxygen tank is a cyan square

def show_stats():
    """Display oxygen, power levels, and health factor on the screen."""
    oxygen_text = font.render(f"Oxygen: {int(oxygen_level)}%", True, WHITE)
    power_text = font.render(f"Power: {int(power_level)}%", True, WHITE)
    health_factor_text = font.render(f"Health: {health_factor}%", True, WHITE)
    weight_text = font.render(f"Weight: {weight:.1f} kg", True, WHITE)
    difficulty_text = font.render(f"Difficulty: {difficulty_level}", True, WHITE)
    screen.blit(oxygen_text, (10, 10))
    screen.blit(power_text, (10, 50))
    screen.blit(health_factor_text, (10, 90))
    screen.blit(weight_text, (10, 130))
    screen.blit(difficulty_text, (10, 170))

def draw_legend():
    """Draw a legend on the right-hand side of the screen with icons and explanations."""
    legend_x = SCREEN_WIDTH - 220  # Legend positioning on the right side
    legend_y = 20
    legend_spacing = 40  # Space between items

    # Legend title
    legend_title = font.render("Legend", True, WHITE)
    screen.blit(legend_title, (legend_x, legend_y))
    
    # Oxygen Legend
    pygame.draw.rect(screen, CYAN, [legend_x, legend_y + legend_spacing, 25, 25])
    oxygen_legend_text = font.render("Oxygen", True, WHITE)
    screen.blit(oxygen_legend_text, (legend_x + 40, legend_y + legend_spacing))

    # Power Legend
    pygame.draw.rect(screen, (0, 128, 255), [legend_x, legend_y + 2 * legend_spacing, 25, 25])
    power_legend_text = font.render("Power", True, WHITE)
    screen.blit(power_legend_text, (legend_x + 40, legend_y + 2 * legend_spacing))

    # Tool Legend
    pygame.draw.rect(screen, GREEN, [legend_x, legend_y + 3 * legend_spacing, 25, 25])
    tool_legend_text = font.render("Tool", True, WHITE)
    screen.blit(tool_legend_text, (legend_x + 40, legend_y + 3 * legend_spacing))

    # Food Legend
    pygame.draw.rect(screen, YELLOW, [legend_x, legend_y + 4 * legend_spacing, 25, 25])
    food_legend_text = font.render("Food", True, WHITE)
    screen.blit(food_legend_text, (legend_x + 40, legend_y + 4 * legend_spacing))

    # System Failure Legend
    pygame.draw.rect(screen, RED, [legend_x, legend_y + 5 * legend_spacing, 25, 25])
    system_legend_text = font.render("Repair Spot", True, WHITE)
    screen.blit(system_legend_text, (legend_x + 40, legend_y + 5 * legend_spacing))

def despawn_item(spawn_time, item_collected, current_time, item_type):
    """Handle item despawn logic after 7 seconds if not collected."""
    if current_time - spawn_time > despawn_time_ms and not item_collected:
        item_collected = True  # Mark item as despawned
        print(f"{item_type} despawned!")
    return item_collected

def respawn_item(item_collected, despawn_time, current_time, respawn_type, respawn_time_ms):
    """Handle item respawn after a dynamic time of despawn."""
    if item_collected and current_time - despawn_time > respawn_time_ms:
        item_collected = False  # Respawn item
        print(f"{respawn_type} respawned!")
    return item_collected

def collect_food():
    """Handle food collection logic."""
    global food_collected, food_x, food_y, weight, health_factor, food_spawn_time, food_despawn_time
    food_collected = True
    food_despawn_time = pygame.time.get_ticks()  # Mark despawn time
    weight += 2  # Increase weight
    weight = min(100, weight)  # Cap weight to 100 kg
    health_factor = min(100, health_factor + 10)  # Increase health and cap it at 100%

def respawn_food():
    """Respawn food after despawn."""
    global food_x, food_y, food_spawn_time
    food_x = random.randint(100, SCREEN_WIDTH - 100)  # Respawn at random position
    food_y = random.randint(spaceship_surface.y + 50, spaceship_surface.y + spaceship_surface.height - 100)
    food_spawn_time = pygame.time.get_ticks()  # Reset spawn time

def collect_oxygen_tank():
    """Handle oxygen tank collection logic."""
    global oxygen_tank_collected, oxygen_tank_x, oxygen_tank_y, oxygen_level, oxygen_tank_spawn_time, oxygen_tank_despawn_time
    oxygen_tank_collected = True
    oxygen_tank_despawn_time = pygame.time.get_ticks()  # Mark despawn time
    oxygen_level = min(100, oxygen_level + 30)  # Increase oxygen level and cap it at 100%

def respawn_oxygen_tank():
    """Respawn oxygen tank after despawn."""
    global oxygen_tank_x, oxygen_tank_y, oxygen_tank_spawn_time
    oxygen_tank_x = random.randint(100, SCREEN_WIDTH - 100)  # Respawn at random position
    oxygen_tank_y = random.randint(spaceship_surface.y + 50, spaceship_surface.y + spaceship_surface.height - 100)
    oxygen_tank_spawn_time = pygame.time.get_ticks()  # Reset spawn time

def collect_power_kit():
    """Handle power kit collection logic."""
    global power_kit_collected, power_kit_x, power_kit_y, power_level, power_kit_spawn_time, power_kit_despawn_time
    power_kit_collected = True
    power_kit_despawn_time = pygame.time.get_ticks()  # Mark despawn time
    power_level = min(100, power_level + 20)  # Increase power level and cap it at 100%

def respawn_power_kit():
    """Respawn power kit after despawn."""
    global power_kit_x, power_kit_y, power_kit_spawn_time
    power_kit_x = random.randint(100, SCREEN_WIDTH - 100)  # Respawn at random position
    power_kit_y = random.randint(spaceship_surface.y + 50, spaceship_surface.y + spaceship_surface.height - 100)
    power_kit_spawn_time = pygame.time.get_ticks()  # Reset spawn time

def all_tools_collected():
    """Check if all tools have been collected."""
    return all(tool[2] for tool in tools)

def repair_system():
    """Repair the system failure if the astronaut is near it and has all tools."""
    global system_failure, oxygen_level, power_level, system_x, system_y
    
    # Check if astronaut is near the failure and has all tools
    if (astronaut_x < system_x + 60 and astronaut_x + 50 > system_x and
        astronaut_y < system_y + 60 and astronaut_y + 70 > system_y and
        all_tools_collected()):
        system_failure = False  # System is repaired
        system_x = random.randint(50, SCREEN_WIDTH - 100)  # Move failure to a new random position
        system_y = random.randint(spaceship_surface.y + 50, spaceship_surface.y + spaceship_surface.height - 100)
        oxygen_level = min(100, oxygen_level + 20)  # Restore oxygen and cap it at 100%
        power_level = min(100, power_level + 20)  # Restore power and cap it at 100%
        respawn_tools()  # Respawn tools after repair

def respawn_tools():
    """Respawn tools in new random positions after each repair."""
    for tool in tools:
        tool[0] = random.randint(100, SCREEN_WIDTH - 100)
        tool[1] = random.randint(spaceship_surface.y + 50, spaceship_surface.y + spaceship_surface.height - 100)
        tool[2] = False  # Mark the tools as not collected

def reset_game():
    """Reset game variables for a new game."""
    global astronaut_x, astronaut_y, oxygen_level, power_level, system_failure, weight, health_factor, game_over_timer, difficulty_level, failure_interval
    astronaut_x = 100
    astronaut_y = spaceship_surface.y + spaceship_surface.height - 70
    oxygen_level = 100
    power_level = 100
    system_failure = False
    weight = 70
    health_factor = 100
    game_over_timer = 200  # Reset game over countdown timer
    difficulty_level = 1  # Reset difficulty
    failure_interval = random.randint(300, 800)  # Reset system failure rate
    respawn_tools()

# Define the missing increase_difficulty function
def increase_difficulty():
    """Increase the difficulty of the game over time."""
    global oxygen_depletion_rate, power_depletion_rate, difficulty_level, failure_interval
    global food_respawn_time_ms, power_kit_respawn_time_ms, oxygen_tank_respawn_time_ms

    # Increase depletion rates and failure rate
    oxygen_depletion_rate += 0.02  # Oxygen depletes faster
    power_depletion_rate += 0.02  # Power depletes faster
    difficulty_level += 1  # Increase difficulty level

    # Make system failures occur more frequently
    failure_interval = max(200, failure_interval - 50)  # Reduce interval, but not below 200 ms

    # Decrease respawn times based on increased difficulty (make items respawn faster)
    food_respawn_time_ms = max(4000, base_respawn_time_ms - (difficulty_level * 500))
    power_kit_respawn_time_ms = max(4000, base_respawn_time_ms - (difficulty_level * 500))
    oxygen_tank_respawn_time_ms = max(4000, base_respawn_time_ms - (difficulty_level * 500))

    print(f"Difficulty increased to level {difficulty_level}! Oxygen/power depletion rates increased.")

# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    if not game_over:
        # Handle controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            astronaut_speed_x -= acceleration
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            astronaut_speed_x += acceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            astronaut_speed_y -= acceleration
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            astronaut_speed_y += acceleration

        # Apply friction to slow down movement
        astronaut_speed_x *= friction
        astronaut_speed_y *= friction

        # Cap speed to max_speed
        astronaut_speed_x = max(-max_speed, min(max_speed, astronaut_speed_x))
        astronaut_speed_y = max(-max_speed, min(max_speed, astronaut_speed_y))

        # Update astronaut's position
        astronaut_x += astronaut_speed_x
        astronaut_y += astronaut_speed_y

        # Keep astronaut within spaceship bounds
        astronaut_x = max(0, min(SCREEN_WIDTH - 50, astronaut_x))
        astronaut_y = max(spaceship_surface.y + 10, min(spaceship_surface.y + spaceship_surface.height - 70, astronaut_y))

        # Constant depletion of oxygen and power levels
        oxygen_level -= oxygen_depletion_rate  # Constant depletion rate for oxygen
        power_level -= power_depletion_rate    # Constant depletion rate for power

        # Gradually decrease weight due to microgravity
        weight -= microgravity_effect
        if weight < low_weight_threshold:
            health_factor -= 0.05  # Gradual health reduction if weight drops too low

        # *Impact on health based on oxygen levels*
        if oxygen_level < critical_oxygen_threshold:
            health_factor -= 0.1  # Health decreases faster when oxygen is low

        # *Impact on health based on power levels*
        if power_level < critical_power_threshold:
            health_factor -= 0.05  # Health decreases if power is low

        # Cap all vital parameters at 100%
        oxygen_level = min(100, oxygen_level)
        power_level = min(100, power_level)
        health_factor = min(100, health_factor)

        # Get current time
        current_time = pygame.time.get_ticks()

        # Despawn items after 7 seconds if not collected
        food_collected = despawn_item(food_spawn_time, food_collected, current_time, "Food")
        power_kit_collected = despawn_item(power_kit_spawn_time, power_kit_collected, current_time, "Power Kit")
        oxygen_tank_collected = despawn_item(oxygen_tank_spawn_time, oxygen_tank_collected, current_time, "Oxygen Tank")

        # Respawn items after dynamic time of despawn
        if food_collected:
            if current_time - food_despawn_time > food_respawn_time_ms:
                respawn_food()  # Respawn food at a new location
                food_collected = False

        if power_kit_collected:
            if current_time - power_kit_despawn_time > power_kit_respawn_time_ms:
                respawn_power_kit()  # Respawn power kit
                power_kit_collected = False

        if oxygen_tank_collected:
            if current_time - oxygen_tank_despawn_time > oxygen_tank_respawn_time_ms:
                respawn_oxygen_tank()  # Respawn oxygen tank
                oxygen_tank_collected = False

        # Update failure timer
        if not system_failure:
            failure_timer += 1

            # Trigger system failure at a random time
            if failure_timer >= failure_interval:
                system_failure = True
                failure_timer = 0  # Reset the timer
                failure_interval = random.randint(300, 800)  # Set a new random interval

        # Apply penalty if system failure is not repaired in time
        if system_failure:
            failure_penalty_timer += 1
            if failure_penalty_timer >= penalty_threshold:
                oxygen_level -= 0.5  # Deplete oxygen faster
                power_level -= 0.5  # Deplete power faster

        # Reset penalty timer when system is repaired
        if not system_failure:
            failure_penalty_timer = 0

        # Repair system if conditions are met
        if system_failure:
            repair_system()

        # Increase difficulty over time
        difficulty_timer += 1
        if difficulty_timer >= difficulty_increase_interval:
            increase_difficulty()  # Call the function to increase difficulty
            difficulty_timer = 0

        # Collect food
        if (astronaut_x < food_x + 20 and astronaut_x + 50 > food_x and
            astronaut_y < food_y + 20 and astronaut_y + 70 > food_y and not food_collected):
            collect_food()

        # Collect power kit
        if (astronaut_x < power_kit_x + 25 and astronaut_x + 50 > power_kit_x and
            astronaut_y < power_kit_y + 25 and astronaut_y + 70 > power_kit_y and not power_kit_collected):
            collect_power_kit()

        # Collect oxygen tank
        if (astronaut_x < oxygen_tank_x + 25 and astronaut_x + 50 > oxygen_tank_x and
            astronaut_y < oxygen_tank_y + 25 and astronaut_y + 70 > oxygen_tank_y and not oxygen_tank_collected):
            collect_oxygen_tank()

        # Collect tools
        for tool in tools:
            if (astronaut_x < tool[0] + 30 and astronaut_x + 50 > tool[0] and
                astronaut_y < tool[1] + 30 and astronaut_y + 70 > tool[1]):
                tool[2] = True  # Mark tool as collected

        # Check for game over conditions
        if oxygen_level <= 0 or power_level <= 0 or health_factor <= 0:
            game_over = True

        # Draw everything
        draw_spaceship()
        draw_astronaut(astronaut_x, astronaut_y)
        for tool in tools:
            if not tool[2]:
                draw_tool(tool[0], tool[1])
        if not food_collected:
            draw_food(food_x, food_y)
        if not power_kit_collected:
            draw_power_kit(power_kit_x, power_kit_y)
        if not oxygen_tank_collected:
            draw_oxygen_tank(oxygen_tank_x, oxygen_tank_y)
        if system_failure:
            draw_system_failure(system_x, system_y)
        show_stats()
        draw_legend()  # Draw the legend on the right-hand side

    else:
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
        press_key_text = font.render("Press R to restart", True, WHITE)
        screen.blit(press_key_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2))

        # Handle game over reset
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_game()
            game_over = False

    pygame.display.update()
    clock.tick(30)

pygame.quit()