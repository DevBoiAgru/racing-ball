import random
import pygame
import math
import time
import os
import traceback
import pickle      # Could've used json, but that makes it easier to cheat
import numpy as np # mf why did you import it and not even use it :skull:
                   # I forgot to uncomment the code after comparing performance :wideskull:
from datetime import datetime

pygame.init()
pygame.mixer.init()


def player_move():
    global can_dash
    global score
    global last_dash
    keys_pressed = pygame.key.get_pressed()
    if (keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]) and ball_vars["alive"]: 
        ball_vars["y_speed"] -= ball_vars["y_acc"]
        ball_vars["fuel"] -= 1/40
        ball_vars["accelerating"] = True
    if (keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]) and ball_vars["alive"]: 
        ball_vars["y_speed"] += ball_vars["y_acc"]
        ball_vars["fuel"] -= 1/40
        ball_vars["accelerating"] = True
    if (keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]) and ball_vars["alive"]: 
        ball_vars["x_speed"] += ball_vars["x_acc"]
        ball_vars["fuel"] -= 1/40
        ball_vars["accelerating"] = True
    if (keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]) and ball_vars["alive"]: 
        ball_vars["x_speed"] -= ball_vars["x_acc"]
        ball_vars["fuel"] -= 1/40
        ball_vars["accelerating"] = True
    if (keys_pressed[pygame.K_LCTRL]) and ball_vars["alive"]:
        ball_vars["x_speed"] = 0
        ball_vars["y_speed"] = 0
    if (keys_pressed[pygame.K_SPACE]) and ball_vars["alive"] and mine["timer"] < 0:
        create_mine()
    if (keys_pressed[pygame.K_h]):
        ball_vars["fuel"] = 9002
    if (keys_pressed[pygame.K_r]) and not ball_vars["alive"]:
        respawn()
    if (keys_pressed[pygame.K_LSHIFT]) and ball_vars["alive"] and (time.time() - last_dash > 2):
        ball_vars["x_speed"] += (int(ball_vars["x_speed"] > 0) - 0.5) * 2 * 10
        ball_vars["y_speed"] += (int(ball_vars["y_speed"] > 0) - 0.5) * 2 * 10
        ball_vars["fuel"] = ball_vars["fuel"] - 3
        create_particles("create_subparticles", 20, {"x": ball_vars["x"], "y": ball_vars["y"]}, 3, 0.12, (100, 100, 255), 36, 5)
        ball_vars["iframes_left"] = 20
        sfx_dash.play()
        can_dash = False
        score += 25
        scoreboard_list.append(["FAST +25", 0])
        last_dash = time.time()

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

def Log(text :str, category: str, location: str):
    """ text: What is the error
        category: Is it a warning, an error, or something else?
        location: what part of the code is causing the error?"""
    try:
        with open(f"{savepath}/log.txt", "r") as logfile:
            logfile.close()
    except FileNotFoundError:
        try:
            os.mkdir(savepath)
            with open(f"{savepath}/log.txt", "+w") as logfile:
                pass
        except FileExistsError:
            with open(f"{savepath}/log.txt", "+w") as logfile:
                pass
    with open(f"{savepath}/log.txt", "a") as logfile:
        logfile.write(f"[{datetime.now()}] : [{category}] : [{location}] : {text} \n")

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

        if (particle["tag"] == "create_subparticles") and frame % 2 == 0:
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

def check_goal():
    global score; global max_enemy_fuel; global max_enemy_timer
    goal_destroyed["y_speed"] += 0.05
    if goal_destroyed["y"] > HEIGHT-12:
        goal_destroyed["y_speed"] = 0
    goal_destroyed["y"] += goal_destroyed["y_speed"]
    create_particles(None, 1, {"x": goal_destroyed["x"]+12, "y": goal_destroyed["y"]+12}, 0, -0.05, (90, 90, 90), 60, 4)

    if (abs(ball_vars["x"] - goal_vars["x"]) < ball_vars["radius"] + goal_vars["radius"]) and (abs(ball_vars["y"] - goal_vars['y']) < ball_vars["radius"] + goal_vars["radius"]):
        create_particles("create_subparticles", 12, {"x": goal_vars["x"], "y": goal_vars["y"]}, 3, 0.07, (255, 255, 0), 50, 6)
        goal_destroyed["x"] = goal_vars["x"] - goal_vars["radius"]
        goal_destroyed["y"] = goal_vars["y"] - goal_vars["radius"]
        goal_destroyed["y_speed"] = 0
        goal_vars["x"] = random.randint(10, WIDTH)
        goal_vars["y"] = random.randint(10, HEIGHT)
        ball_vars["fuel"] = min(60, ball_vars["fuel"] + 6.3)
        score += 127
        draw_floatertext(f"+{127}", 20, 2, (ball_vars["x"], ball_vars["y"]), (100,100,100))
        sfx_explosion.play()
        max_enemy_fuel *= 1.125
        scoreboard_list.append(["Destroyed +127", 0])
        max_enemy_timer *= 0.925
        max_enemy_timer += 0.2

def create_enemies():
    global enemy_timer; global max_enemy_fuel; global max_enemy_timer
    enemy_timer -= 1/60
    if enemy_timer <= 0 and ball_vars["alive"]:
        sfx_enemyspawn.play()
        enemy_timer = max_enemy_timer
        enemy_list.append({"x": 500, "y": 500, "x_speed": 0, "y_speed": 0, "x_acc": 0.2, "y_acc": 1/3, "fall_acc": 0.2, "radius": 6, "fuel": round(max_enemy_fuel, 0), "alive": True, "done": False})
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
                score += 107
                draw_floatertext(f"+{107}", 20, 2, (ball_vars["x"], ball_vars["y"]), (100,100,100))
                scoreboard_list.append(["Slaughtered +107", 0])
           
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
            enemy["x_speed"] *= -0.6

        # left border
        if enemy["x"] < enemy["radius"]:
           enemy["x"] = enemy["radius"]
           enemy["x_speed"] *= -0.6

       # top border
        if enemy["y"] < enemy["radius"]:
           enemy["y"] = enemy["radius"]
           enemy["y_speed"] *= -0.6

      # bottom border
        if enemy["y"]  > HEIGHT - enemy["radius"]*2:
            enemy["y"] = HEIGHT - enemy["radius"]*2
            enemy["y_speed"] *= -0.6
            enemy["x_speed"] *= 0.99

def check_enemies():
    global score
    player_speed = math.sqrt(ball_vars["x_speed"]**2 + ball_vars["y_speed"]**2)
    for enemy in enemy_list:
        if ((abs(ball_vars["x"] - enemy["x"]) < ball_vars["radius"] + enemy["radius"]) and (abs(ball_vars["y"] - enemy['y']) < ball_vars["radius"] + enemy["radius"]) and enemy["alive"]) and ball_vars["iframes_left"] <= 0:
            if player_speed > 20:
                enemy["alive"] = False  
                create_particles(None, 8, {"x": enemy["x"], "y": enemy["y"]}, 4, 0, (20, 52, 100), 50, 5)
                sfx_enemydead.play()
                enemy["x_speed"] = ball_vars["x_speed"]
                enemy["y_speed"] = ball_vars["y_speed"]
                ball_vars["fuel"] += 12.5
                score += 352
                draw_floatertext(f"+{352}", 20, 2, (ball_vars["x"], ball_vars["y"]), (100,100,100))
                scoreboard_list.append(["DASHED +352", 0])
            else:
                ball_vars["fuel"] /= 1.33
                if ball_vars["alive"]:
                    sfx_hit.play()  
                    create_particles(None, 10, {"x": ball_vars["x"], "y": ball_vars["y"]}, 4, 0.15, (255, 255 ,255), 60, 5)
                    score -= 91
                    draw_floatertext(f"-{91}", 20, 2, (ball_vars["x"], ball_vars["y"]), (100,100,100))
                    scoreboard_list.append(["skill issue -42", 0])

                    ball_vars["iframes_left"] = 30

def create_mine():
    mine["x"] = ball_vars["x"] - ball_vars["radius"]
    mine["y"] = ball_vars["y"] - ball_vars["radius"]
    mine["timer"] = 100

def check_mine():
    global score
    mine["timer"] -= 1
    if (mine["timer"] % 20 == 0) and (mine["timer"] > 0):
        sfx_beep.play()
    if mine["timer"] == 0:
        for enemy in enemy_list:
            if ((mine["x"] - enemy["x"])**2 + (mine["y"] - enemy["y"])**2)**0.5 < 133:
                enemy["alive"] = False
                enemy["fuel"] = 0
                score += 411
                scoreboard_list.append(["Blasted +411", 0])
                draw_floatertext("+411", 20, 2, (enemy["x"], enemy["y"]))
        create_particles(None, 1, {"x": mine["x"], "y": mine["y"]}, 0, 0, (255, 180, 0), 10, 133) 
        sfx_mine.play()
        mine["x"] = -500
        mine["y"] = -8000

def respawn():
    global max_enemy_fuel
    global score
    global enemy_list
    global max_enemy_timer
    ball_vars["fuel"] = 30
    ball_vars["alive"] = True
    ball_vars["x"] = WIDTH/2
    ball_vars["y"] = HEIGHT/2
    music.play(-1)
    max_enemy_fuel = 5
    max_enemy_timer = 4
    enemy_list = []
    score = 0
    music.stop()
    music.play(-1)
    LoadGame()

def check_fps():
    global fps_string
    global last_fps_check_time
    current_time = time.time()
    time_delta = current_time - last_fps_check_time
    fps = 1/time_delta
    fps_list.append(fps)
    if len(fps_list) > 256: fps_list.pop(0)
    # fps_string = f"time since last frame: {round(time_delta, 3)} ({round(fps, 1)} fps; {round(sum(fps_list)/256, 1)} average; {round(max(fps_list), 1)} max; {round(min(fps_list), 1)} min)"
    fps_string = f"time since last frame: {round(time_delta, 3)} ({round(fps, 1)} fps; {round(np.mean(fps_list), 1)} average; {round(max(fps_list), 1)} max; {round(min(fps_list), 1)} min)"
    last_fps_check_time = current_time

def LoadGame() -> dict:
    try:
        with open(f"{savepath}/save.balls", "rb") as savefile:
            try:
                global HighestScore
                savedata = pickle.load(savefile)

                HighestScore = savedata["playerdata"]["HighScore"]
                
                Log ("Loading data from save file", "UTILITY", "LoadGame")
            except Exception as e:
                Log (f"{traceback.format_exc}", "ERROR", "LoadGame")
                
    except FileNotFoundError:
        Log ("No save file found", "WARNING", "LoadGame")


def SaveGame(HighScore :int) -> None:
    try:
        with open(f"{savepath}/save.balls", "rb") as savefile:
            savefile.close()
    except FileNotFoundError:
        Log("Save file does not exist.", "WARNING", "SaveGame")
        try:
            os.mkdir(savepath)
            Log("Creating save folder", "UTLITIY", "SaveGame")
        except FileExistsError:
            Log("Save folder exists, but the file does not.", "WARNING", "SaveGame")

        with open(f"{savepath}/save.balls", "+wb") as savefile:
            Log("Creating log file", "UTLITIY", "SaveGame")
            savefile.close()
    
    with open(f"{savepath}/save.balls", "wb") as savefile:
        Log("Creating save file", "UTILITY", "SaveGame")
        savedata = {}
        savedata["playerdata"] = {"HighScore" : HighScore}
        pickle.dump(savedata, savefile)


def update_scoreboard():
    i = 0
    for item in scoreboard_list: 
        item[1] += 1
        if item[1] > 120:
            scoreboard_list.pop(i)

        text = font.render(item[0], False, (100, 100, 100))
        window.blit(text, (WIDTH-230, 95 + 15*i))
        i += 1

global WIDTH, HEIGHT; WIDTH, HEIGHT = 1280, 720
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("I wokup inanu bugatti")

ball_sprite        = pygame.image.load("assets/sprites/ball.png")
ball_sprite        = pygame.image.load("assets/sprites/ball.png")
ball_active_sprite = pygame.image.load("assets/sprites/ball_active.png")
goal_sprite        = pygame.image.load("assets/sprites/goal.png")
enemy_sprite       = pygame.image.load("assets/sprites/enemy.png")
enemy_dead_sprite  = pygame.image.load("assets/sprites/enemy_dead.png")
destroyed_goal_sprite = pygame.image.load("assets/sprites/goal_destroyed.png")
mine_sprite        = pygame.image.load("assets/sprites/mine.png")

# Background, no shit sherlock
bgscale = 1 # How big the background is, no shit sherlock
bgimage = pygame.transform.scale_by(pygame.image.load("assets/sprites/background.png"), bgscale)

ball_vars = {"x": WIDTH/2, "y": HEIGHT/2, "fuel": 30, "x_speed": 0, "y_speed": 0, "x_acc": 1/3, "y_acc": 0.75, "self_gravity": 0.2, "alive": True, "radius": 6, "accelerating": False, "iframes_left": 0}
goal_vars = {"x": random.randint(10, HEIGHT-10), "y": random.randint(10, HEIGHT-10), "radius": 12}
fuel_consumption = 1/240
can_dash = True
enemy_list = []
global enemy_timer; enemy_timer = 1             # Why are these marked as global if they are already global
global max_enemy_timer; max_enemy_timer = 4
global max_enemy_fuel; max_enemy_fuel = 5
particle_list = []
ball_trail_list = []
global score; score = 0
show_floating_text_for = 0
goal_destroyed = {"x": -500, "y": -8000, "y_speed": 0}
mine = {"x": -500, "y": -8000, "timer": -1}
fps_list = []
global last_fps_check_time; last_fps_check_time = 0
scoreboard_list = []
fps_string = ""
global last_dash; last_dash = 0
global frame; frame = 0

savepath = "Saves"
HighestScore = 0

# Floating text, no shit sherlock
floating_text = None    # Set text to none because we don't need any text at startup, no shit sherlock
floating_end = 0        # Default kill time for the text. This is overwritten when the function is called
dead_font = pygame.font.SysFont("courier", 50)
respawn_text = dead_font.render("Dead. Press 'R' to respawn", False, (100, 100, 100))

# Initialize audios
sfx_bounce     = pygame.mixer.Sound("assets/sfx/bounce.wav")
sfx_dash       = pygame.mixer.Sound("assets/sfx/dash.wav")
sfx_enemydead  = pygame.mixer.Sound("assets/sfx/enemydead.wav")
sfx_enemyspawn = pygame.mixer.Sound("assets/sfx/enemyspawn.wav")
sfx_explosion  = pygame.mixer.Sound("assets/sfx/explosion.wav")
sfx_hit        = pygame.mixer.Sound("assets/sfx/hit.wav")
sfx_mine       = pygame.mixer.Sound("assets/sfx/mine.wav")
sfx_beep       = pygame.mixer.Sound("assets/sfx/beep.wav")
music          = pygame.mixer.Sound("assets/sfx/Electro-Light - Symbolism [NCS Release].mp3")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 18)

running = True
LoadGame()
music.play(-1)
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # window.fill((0, 0, 0)) # Do we still need this? Lmfao no but let's keep this line for funni

    # Blit background, no shit sherlock
    window.blit(bgimage, (0,0))

    ball_vars["accelerating"] = False
    ball_vars["fuel"] -= fuel_consumption
    if ball_vars["fuel"] <= 0: 
        ball_vars["alive"] = False
        window.blit(respawn_text, (WIDTH/2 - 400, HEIGHT/2))
        if score > HighestScore:
            SaveGame(score)
        music.stop()
    else: ball_vars["alive"] = True

    check_fps()
    pygame.draw.circle(window, (24, 16, 0), (mine["x"], mine["y"]), 100)
    player_move()
    check_player_collision()
    check_goal()
    update_enemies()
    check_enemies()
    create_enemies()    
    check_mine()
    update_floatertext()
    update_scoreboard()

    # High score
    highscoretext = font.render(f"High score: {HighestScore}", False, (100,100,100))
    window.blit(pygame.transform.scale_by(highscoretext, 1.2), (WIDTH-230, 50))
    # Simple scoreboard no shit sherlock
    scoretext = font.render(f"Score: {score}", False, (100,100,100))
    window.blit(pygame.transform.scale_by(scoretext, 1.2), (WIDTH-230, 70))

    # Frame rate information
    fpstext = font.render(fps_string, False, (255,255,255))
    window.blit(fpstext, (300, 10))

    # Devboi do not fucking remove this loop or i will beat your skull into dust with a lead pipe
    # I will. <- this line was written by a person with massive skill issues
    #              ^ That line was written by a person with even bigger skill issues
    strings = [
         "║║        ║ ╚═╗       ║",
         '║║[ YELLOW IS FUEL ]  ║',
         '║║ [ RED ARE THREAT ]═╝',
         '║╚══[ GOAL:  SURVIVE ]',
         '║ ',
        f'╠═[ x ]═[ {int(ball_vars["x"])} ]',
        f'╠═[ y ]═[ {int(ball_vars["y"])} ]',
        f'╠═[ f ]═[ {max(round(ball_vars["fuel"], 1), 0)} ] ← !!',
        f'╠═[ X ]═[ {round(ball_vars["x_speed"], 2)} ]',
        f'╠═[ Y ]═[ {round(ball_vars["y_speed"], 2)} ]',
        f'╠═[ i ]═[ {max(ball_vars["iframes_left"], 0)} ]',
        f'╠═[ E ]═[ {len(enemy_list)} ]',
        f'╠═[ e ]═[ {round(enemy_timer, 2)} ]',
        f'╠═[ m ]═[ {round(max_enemy_fuel, 1)} ]',
        f'╠═[ M ]═[ {round(max_enemy_timer, 2)} ]',
        f'╠═[ p ]═[ {len(particle_list)} ]',
         '╝ '
    ]
    for string in strings:
        text = font.render(string, False, (100, 100, 100))
        window.blit(text, (0, 20 * (strings.index(string) + 1) - 20))

    window.blit(destroyed_goal_sprite, (goal_destroyed["x"], goal_destroyed["y"]))
    ball_trail_update()
    particle_update()

    window.blit(goal_sprite, (goal_vars["x"] - goal_vars["radius"], goal_vars["y"] - goal_vars["radius"]))
    window.blit(mine_sprite, (mine["x"]-5, mine["y"]-5))
    if ball_vars["accelerating"]: bs = ball_active_sprite
    else: bs = ball_sprite
    window.blit(bs, (ball_vars["x"] - ball_vars["radius"], ball_vars["y"] - ball_vars["radius"]))

    frame += 1
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

"""
TODO add kill combo bonuses
TODO add a bossfight (fish boss real)
TODO improve the visual effects
TODO fix the mine explosion behaving weirdly
TODO stylize the scoreboard
TODO add enemy variety
TODO add background stains (when enemies get killed, goals destroyed, dashes dashed etc.) # Crazy
------------------------------------
DOING refactor the code to make it more readable
DOING add variety to gameplay (somehow idk) 
------------------------------------
DONE add a way to respawn LIKE WHY DIDN'T WE ADD THIS BEFORE
DONE add scoreboard
DONE improve ball handling
DONE add a simple background instead of the black void
DONE add sfx and music
"""
# j <- literally the only instance of this letter in the entire code :skull: