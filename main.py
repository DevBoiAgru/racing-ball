import random
import pygame
from math import sqrt
import os
import time

pygame.init()
pygame.mixer.init()


def player_move():
    keys_pressed = pygame.key.get_pressed()
    if (keys_pressed[pygame.K_UP   ] or keys_pressed[pygame.K_w]) and ball_vars["alive"]: 
        ball_vars["y_speed"] -= ball_vars["y_acc"]
        ball_vars["fuel"] -= 1/40
        ball_vars["accelerating"] = True
    if (keys_pressed[pygame.K_DOWN ] or keys_pressed[pygame.K_s]) and ball_vars["alive"]: 
        ball_vars["y_speed"] += ball_vars["y_acc"]
        ball_vars["fuel"] -= 1/40
        ball_vars["accelerating"] = True
    if (keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]) and ball_vars["alive"]: 
        ball_vars["x_speed"] += ball_vars["x_acc"]
        ball_vars["fuel"] -= 1/40
        ball_vars["accelerating"] = True
    if (keys_pressed[pygame.K_LEFT ] or keys_pressed[pygame.K_a]) and ball_vars["alive"]: 
        ball_vars["x_speed"] -= ball_vars["x_acc"]
        ball_vars["fuel"] -= 1/40
        ball_vars["accelerating"] = True

    ball_vars["y_speed"] += ball_vars["self_gravity"]
    ball_vars["x"] += ball_vars["x_speed"]
    ball_vars["y"] += ball_vars["y_speed"]
    ball_vars["iframes_left"] -= 1

def create_particles(tag, amount, pos, max_speed, fall_acc, color, max_age, radius):
    for _ in range(random.randint(int(amount/2), amount)):
        particle = {"x": pos["x"]+random.randint(-radius, radius), "y": pos["y"]+random.randint(-radius, radius), "x_speed": random.randint(-max_speed*10, max_speed*10)/10, "y_speed": random.randint(-max_speed*10, max_speed*10)/10, "fall_acc": fall_acc, "age": 0, "tag": tag, "color": color, "max_age": max_age, "radius": radius}
        particle_list.append(particle)

def check_player_collision():
    # right border
    if ball_vars["x"]  > WIDTH - ball_vars["radius"]:
        ball_vars["x"] = WIDTH - ball_vars["radius"]
        ball_vars["x_speed"] *= -0.6
        if ball_vars["x_speed"] < -0.4:
            create_particles(
                None, 4, {"x": ball_vars["x"], "y": ball_vars["y"]}, 3, 0.12, (255, 255, 255), 36, 5)
            sfx_bounce.play()
            

    # left border
    if ball_vars["x"]  < ball_vars["radius"]:
        ball_vars["x"] = ball_vars["radius"]
        ball_vars["x_speed"] *= -0.6
        if ball_vars["x_speed"] > 0.4:
            create_particles(
                None, 4, {"x": ball_vars["x"], "y": ball_vars["y"]}, 3, 0.12, (255, 255, 255), 36, 5)
            sfx_bounce.play()
            

    # top border
    if ball_vars["y"]  < ball_vars["radius"]:
        ball_vars["y"] = ball_vars["radius"]
        ball_vars["y_speed"] *= -0.6
        if ball_vars["y_speed"] > 0.4:
            create_particles(
                None, 4, {"x": ball_vars["x"], "y": ball_vars["y"]}, 3, 0.12, (255, 255, 255), 36, 5)
            sfx_bounce.play()

    # bottom border
    if ball_vars["y"]  > HEIGHT - ball_vars["radius"]:
        ball_vars["y"] = HEIGHT - ball_vars["radius"]
        ball_vars["y_speed"] *= -0.6
        if ball_vars["x_speed"] > 0: ball_vars["x_speed"] -= 0.01
        if ball_vars["x_speed"] < 0: ball_vars["x_speed"] += 0.01
        if ball_vars["y_speed"] < -0.4:
            create_particles(
                None, 4, {"x": ball_vars["x"], "y": ball_vars["y"]}, 3, 0.12, (255, 255, 255), 36, 5)
            sfx_bounce.play()

def dash_update():
    global can_dash
    speed_multiplier = 3 # How much of a speed boost the dash gives
    keys_pressed = pygame.key.get_pressed()
    if (keys_pressed[pygame.K_LSHIFT]) and ball_vars["alive"] and ball_vars["fuel"] > 3:
        default_speed = (ball_vars["x_speed"], ball_vars["y_speed"])
        ball_vars["x_speed"] = default_speed[0] * speed_multiplier
        ball_vars["y_speed"] = default_speed[1] * speed_multiplier
        ball_vars["fuel"] = ball_vars["fuel"] - 3
        create_particles("create_subparticles", 20, {"x": ball_vars["x"], "y": ball_vars["y"]}, 3, 0.12, (100, 100, 255), 36, 5)
        ball_vars["iframes_left"] = 20
        sfx_dash.play()
        
        can_dash = False

def draw_floatertext(text :str = "Lorem ipsum", size :int = 20, duration :int = 2, position :tuple = (0,0), color :tuple = (100,100,100)):
    global floating_text, floating_end

    fontrender = pygame.font.SysFont("courier", size)
    rend = fontrender.render(text, False, color)
    floating_text = (rend, position)
    floating_end = pygame.time.get_ticks() + duration*1000 # 1000 milliseconds = 1 second


def update_floatertext():
    if floating_text and pygame.time.get_ticks() < floating_end: 
        window.blit(floating_text[0], floating_text[1])

def particle_update():
    for particle in particle_list:
        particle["age"] += int(random.random() < 0.85)
        if particle["age"] > particle["max_age"]:
            particle_list.pop(particle_list.index(particle))
    
        particle["y_speed"] += particle["fall_acc"]
        particle["x"] += particle["x_speed"]
        particle["y"] += particle["y_speed"]

        if particle["tag"] == "create_subparticles":
            particle_list.append({"x": particle["x"], "y": particle["y"], "x_speed": 0, "y_speed": 0, "fall_acc": 0, "age": int(particle["age"]/2), "tag": None, "color": particle["color"], "max_age": particle["max_age"]*1.5, "radius": particle["radius"]})

        pygame.draw.circle(window, (max(int(particle["color"][0] - particle["color"][0] * (particle["age"] / particle["max_age"])), 0), 
                                    max(int(particle["color"][1] - particle["color"][1] * (particle["age"] / particle["max_age"] * 1.5)), 0), 
                                    max(int(particle["color"][2] - particle["color"][2] * (particle["age"] / particle["max_age"] * 2.0)), 0)),
                                    (particle["x"], particle["y"]), particle["radius"] - particle["radius"] * (particle["age"] / particle["max_age"]))

def ball_trail_update():
    if ball_vars["alive"] and ball_vars["accelerating"]: ball_trail_list.append({"x": ball_vars["x"], "y": ball_vars["y"], "age": 0, "active": True})
    elif ball_vars["alive"] and not ball_vars["accelerating"]: ball_trail_list.append({"x": ball_vars["x"], "y": ball_vars["y"], "age": 0, "active": False})
    for ball_trail in ball_trail_list:
        ball_trail["age"] += 1
        if ball_trail["age"] > 9:
            ball_trail_list.pop(ball_trail_list.index(ball_trail))
        if ball_trail["active"]: pygame.draw.circle(window, (max(0, 255 - 24 * ball_trail["age"]), max(0, 255 - 48 * ball_trail["age"]), 0), (ball_trail["x"], ball_trail["y"]), 4 - 0.36 * ball_trail["age"])
        else: pygame.draw.circle(window, (max(0, 31 - 2 * ball_trail["age"]), max(0, 31 - 2 * ball_trail["age"]), 0), (ball_trail["x"], ball_trail["y"]), 4 - 0.36 * ball_trail["age"])

def image(name):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_directory, name)
    return pygame.image.load(image_path)

def check_goal():
    global score; global max_enemy_fuel
    if (abs(ball_vars["x"] - goal_vars["x"]) < ball_vars["radius"] + goal_vars["radius"]) and (abs(ball_vars["y"] - goal_vars['y']) < ball_vars["radius"] + goal_vars["radius"]):
        create_particles("create_subparticles", 12, {"x": goal_vars["x"], "y": goal_vars["y"]}, 3, 0.07, (255, 255, 0), 50, 6)
        goal_vars["x"] = random.randint(10, WIDTH)
        goal_vars["y"] = random.randint(10, HEIGHT)
        ball_vars["fuel"] = min(60, ball_vars["fuel"] + 6.3)
        score += 127
        draw_floatertext(f"+{127}", 20, 2, (ball_vars["x"], ball_vars["y"]), (100,100,100))
        sfx_explosion.play()
        max_enemy_fuel *= 1.125

def create_enemies():
    global enemy_timer; global max_enemy_fuel
    enemy_timer -= 1/60
    if enemy_timer <= 0 and ball_vars["alive"]:
        sfx_enemyspawn.play()
        enemy_timer = 6
        enemy_list.append({"x": 500, "y": 500, "x_speed": 0, "y_speed": 0, "x_acc": 0.1, "y_acc": 0.25, "fall_acc": 0.2, "radius": 6, "fuel": round(max_enemy_fuel, 0), "alive": True, "done": False})
        create_particles(None, 14, {"x": enemy_list[-1]["x"], "y": enemy_list[-1]["y"]}, 4, 0, (200, 0, 0), 50, 5)

def update_enemies():
    global score; global max_enemy_fuel
    for enemy in enemy_list:
        enemy["fuel"] -= 1/60
        if enemy["fuel"] <= 0:
            enemy["alive"] = False
            if enemy["done"] == False:
                create_particles(None, 8, {"x": enemy["x"], "y": enemy["y"]}, 4, 0, (20, 52, 100), 50, 5)
                sfx_enemydead.play()
                enemy["done"] = True
                score += 49
                draw_floatertext(f"+{49}", 20, 2, (ball_vars["x"], ball_vars["y"]), (100,100,100))
           
        if (ball_vars["x"] - enemy["x"] < enemy["radius"] + ball_vars["radius"]) and enemy["alive"]:
           enemy["x_speed"] -= enemy["x_acc"]
        elif (enemy["x"] - ball_vars["x"] < enemy["radius"] + ball_vars["radius"]) and enemy["alive"]: 
           enemy["x_speed"] += enemy["x_acc"]

        if (ball_vars["y"] - enemy["y"] < enemy["radius"] + ball_vars["radius"]) and enemy["alive"]:
           enemy["y_speed"] -= enemy["y_acc"]
        elif (enemy["y"] - ball_vars["y"] < enemy["radius"] + ball_vars["radius"]) and enemy["alive"]: 
           enemy["y_speed"] += enemy["y_acc"]
        if not enemy["alive"]: enemy["y_speed"] += enemy["fall_acc"]
        
        enemy["x"] += enemy["x_speed"]
        enemy["y"] += enemy["y_speed"]
        check_enemy_collision()

        if (not enemy["alive"]) and (abs(enemy["y_speed"]) < 0.3) and (abs(enemy["x_speed"]) < 0.3):
            enemy_list.pop(enemy_list.index(enemy))
        if not enemy["alive"]:
            window.blit(enemy_dead_sprite, (enemy["x"], enemy["y"]))
        else:
            window.blit(enemy_sprite, (enemy["x"], enemy["y"]))

def check_enemy_collision():
    for enemy in enemy_list:
    # right border
        if enemy["x"]  > WIDTH - enemy["radius"]:
            enemy["x"] = WIDTH - enemy["radius"]
            if abs(enemy["x_speed"]) > 0.5:
                sfx_bounce.play()
            enemy["x_speed"] *= -0.6

        # left border
        if enemy["x"] < enemy["radius"]:
           enemy["x"] = enemy["radius"]
           if abs(enemy["x_speed"]) > 0.5:
                sfx_bounce.play() 
           enemy["x_speed"] *= -0.6

       # top border
        if enemy["y"] < enemy["radius"]:
           enemy["y"] = enemy["radius"]
           if abs(enemy["y_speed"]) > 0.5:
                sfx_bounce.play()
           enemy["y_speed"] *= -0.6

      # bottom border
        if enemy["y"]  > HEIGHT - enemy["radius"]*2:
            enemy["y"] = HEIGHT - enemy["radius"]*2
            if abs(enemy["y_speed"]) > 0.5:
                sfx_bounce.play()
            enemy["y_speed"] *= -0.6
            enemy["x_speed"] *= 0.99

def check_enemies():
    global score
    player_speed = sqrt(ball_vars["x_speed"]**2 + ball_vars["y_speed"]**2)
    for enemy in enemy_list:
        if ((abs(ball_vars["x"] - enemy["x"]) < ball_vars["radius"] + enemy["radius"]) and (abs(ball_vars["y"] - enemy['y']) < ball_vars["radius"] + enemy["radius"]) and enemy["alive"]) and ball_vars["iframes_left"] <= 0:
            if player_speed > 10:
                enemy["alive"] = False  
                create_particles(None, 8, {"x": enemy["x"], "y": enemy["y"]}, 4, 0, (20, 52, 100), 50, 5)
                sfx_enemydead.play()
                ball_vars["x_speed"] *= -0.2
                ball_vars["y_speed"] *= -0.2
                ball_vars["fuel"] += 12.5
                score += 357
                draw_floatertext(f"+{357}", 20, 2, (ball_vars["x"], ball_vars["y"]), (100,100,100))
            else:
                ball_vars["fuel"] /= 1.33
                if ball_vars["alive"]:
                    sfx_hit.play()  
                    create_particles(None, 10, {"x": ball_vars["x"], "y": ball_vars["y"]}, 4, 0.15, (255, 255 ,255), 60, 5)
                    score -= 42
                    draw_floatertext(f"-{42}", 20, 2, (ball_vars["x"], ball_vars["y"]), (100,100,100))

                    ball_vars["iframes_left"] = 30

global WIDTH, HEIGHT; WIDTH, HEIGHT = 1280, 720
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball game")

ball_sprite = image("assets/ball.png")
ball_active_sprite = image("assets/ball_active.png")
goal_sprite = image("assets/goal.png")
enemy_sprite = image("assets/enemy.png")
enemy_dead_sprite = image("assets/enemy_dead.png")

ball_vars = {"x": WIDTH/2, "y": HEIGHT/2, "fuel": 30, "x_speed": 0, "y_speed": 0, "x_acc": 0.2, "y_acc": 0.5, "self_gravity": 0.2, "alive": True, "radius": 6, "accelerating": False, "iframes_left": 0}
goal_vars = {"x": random.randint(10, HEIGHT-10), "y": random.randint(10, HEIGHT-10), "radius": 12}
fuel_consumption = 1/360
can_dash = True
enemy_list = []
global enemy_timer; enemy_timer = 1
global max_enemy_fuel; max_enemy_fuel = 4
particle_list = []
ball_trail_list = []
global score; score = 0
show_floating_text_for = 0

# Floating text
floating_text = None    # Set text to none because we don't need any text at startup
floating_end = 0        # Default kill time for the text. This is overwritten when the function is called

# Initialize audios

sfx_bounce     =  pygame.mixer.Sound("assets/bounce.wav")
sfx_dash       =  pygame.mixer.Sound("assets/dash.wav")
sfx_enemydead  =  pygame.mixer.Sound("assets/enemydead.wav")
sfx_enemyspawn =  pygame.mixer.Sound("assets/enemyspawn.wav")
sfx_explosion  =  pygame.mixer.Sound("assets/explosion.wav")
sfx_hit        =  pygame.mixer.Sound("assets/hit.wav")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 18)

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    window.fill((0, 0, 0))

    ball_vars["accelerating"] = False
    ball_vars["fuel"] -= fuel_consumption
    if ball_vars["fuel"] <= 0: ball_vars["alive"] = False
    else: ball_vars["alive"] = True

    if can_dash:
        dash_update()
        last_dash = time.perf_counter()
    else:
        if time.perf_counter() - last_dash > 1.5:
            can_dash = True

    player_move()
    check_player_collision()
    check_goal()
    update_enemies()
    check_enemies()
    create_enemies()
    update_floatertext()

    strings = [
         "║",
         '╠═[ COLLECT YELLOW ORBS FOR FUEL ]',
         '║ [  AVOID RED BALLS OR GO FAST  ]',
         '║ ',
        f'╠═[ x ]═[ {int(ball_vars["x"])} ]',
        f'╠═[ y ]═[ {HEIGHT - int(ball_vars["y"])} ]',
        f'╠═[ f ]═[ {max(round(ball_vars["fuel"], 1), 0)} ] ← !',
        f'╠═[ X ]═[ {round(ball_vars["x_speed"], 2)} ]',
        f'╠═[ Y ]═[ {-round(ball_vars["y_speed"], 2)} ]',
        f'╠═[ i ]═[ {max(ball_vars["iframes_left"], 0)} ]',
        f'╠═[ E ]═[ {len(enemy_list)} ]',
        f'╠═[ e ]═[ {round(enemy_timer, 2)} ]',
        f'╠═[ m ]═[ {round(max_enemy_fuel, 1)} ]',
        f'╠═[ S ]═[ {score} ]',
        f'╠═[ p ]═[ {len(particle_list)} ]',
         '╝ '
    ]
    for string in strings:
        text = font.render(string, False, (100, 100, 100))
        window.blit(text, (0, 20 * (strings.index(string) + 1) - 20))

    ball_trail_update()
    particle_update()

    window.blit(goal_sprite, (goal_vars["x"] - goal_vars["radius"], goal_vars["y"] - goal_vars["radius"]))
    if ball_vars["accelerating"]: bs = ball_active_sprite
    else: bs = ball_sprite
    window.blit(bs, (ball_vars["x"] - ball_vars["radius"], ball_vars["y"] - ball_vars["radius"]))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

"""
TODO improve the visual effects
TODO add a simple background instead of the black void
TODO refactor the code to make it more readable
TODO enlarge balls
TODO improve gameplay (somehow idk)
TODO make the game more pixel-y
------------------------------------
DOING add sfx and music
"""