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
music = pygame.mixer.music

class Ball:
    def __init__(self, is_player: bool = False, radius: int = 6, ball_active_sprite: pygame.surface = None, ball_non_active_sprite: pygame.surface = None,initial_location: tuple = (1280/2, 720/2), fuel: float = 30, iframes: int = 0):
        self.x = initial_location[0]
        self.y = initial_location[1]
        self.fuel = fuel
        self.x_speed = 0
        self.y_speed = 0
        self.x_acc = 1/3
        self.y_acc = 0.75
        self.gravity = 0.2
        self.alive = True
        self.radius = radius
        self.accelerating = True
        self.iframes_left = 0
        self.active_sprite = ball_active_sprite
        self.inactive_sprite = ball_non_active_sprite
        self.CanDash = True
        self.Is_Player = is_player
        self.iframes = iframes
        self.PygameEvents = []
        
    def check_collision(self):
        # right border
        if self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.x_speed *= -0.6
            if self.x_speed < -0.4 and self.Is_Player:
                create_particles(None, 4, {"x": self.x, "y": self.y}, 3, 0.12, (255, 255, 255), 36, 5)
                sfx_bounce.play()

        # left border
        if self.x < self.radius:
            self.x = self.radius
            self.x_speed *= -0.6
            if self.x_speed > 0.4 and self.Is_Player:
                create_particles(None, 4, {"x": self.x, "y": self.y}, 3, 0.12, (255, 255, 255), 36, 5)
                sfx_bounce.play()

        # top border
        if self.y < self.radius:
            self.y = self.radius
            self.y_speed *= -0.6
            if self.y_speed > 0.4 and self.Is_Player:
                create_particles(None, 4, {"x": self.x, "y": self.y}, 3, 0.12, (255, 255, 255), 36, 5)
                sfx_bounce.play()

        # bottom border
        if self.y > HEIGHT - self.radius:
            self.y = HEIGHT - self.radius
            self.y_speed *= -0.6
            if self.x_speed > 0:
                self.x_speed -= 0.01
            if self.x_speed < 0:
                self.x_speed += 0.01
            if self.y_speed < -0.4 and self.Is_Player:
                create_particles(None, 4, {"x": self.x, "y": self.y}, 3, 0.12, (255, 255, 255), 36, 5)
                sfx_bounce.play()

    def respawn(self):
        global max_enemy_fuel, score, enemy_list, max_enemy_timer
        self.fuel = 30
        self.alive = True
        self.x = WIDTH/2
        self.y = HEIGHT/2
        self.x_speed = 0
        self.y_speed = 0
        max_enemy_fuel = 5
        max_enemy_timer = 4
        enemy_list = []
        score = 0
        pygame.mixer.music.unpause()
        load_game()

    def handle_movement(self):
        global score
        global last_dash
        for event in self.PygameEvents:
            if event.type == pygame.KEYDOWN and event.key == (pygame.K_LSHIFT) and self.alive:
                self.x_speed += (int(self.x_speed > 0) - 0.5) * 2 * 10
                self.y_speed += (int(self.y_speed > 0) - 0.5) * 2 * 10
                self.fuel = self.fuel - 3
                create_particles("create_subparticles", 20, {"x": self.x, "y": self.y}, 3, 0.12, (100, 100, 255), 36, 5)
                self.iframes = max(self.iframes + 8, 8)
                sfx_dash.play()
                score += 25
                scoreboard_list.append(["FAST +25", 0])
            
            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_SPACE) and self.alive and mine["timer"] < -45:
                create_mine()
        
            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_r) and not self.alive:
                self.respawn()

            # music switcher (very cool)
            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_1):
                music.stop()
                music.unload()
                music.load("assets/sfx/Lethal company boombox song 5.mp3")
                music.play(loops=-1)
            
            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_2):
                music.stop()
                music.unload()
                music.load("assets/sfx/Electro-Light - Symbolism [NCS Release].mp3")
                music.play(loops=-1, start=3)

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_3):
                music.stop()
                music.unload()
                music.load("assets/sfx/HL2 Apprehension and Evasion.mp3")
                music.play(loops=-1, start=10)

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_4):
                music.stop()
                music.unload()
                music.load("assets/sfx/HL Credits Closing Theme.mp3")
                music.play(loops=-1)

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_5):
                music.stop()
                music.unload()
                music.load("assets/sfx/Stray Error-22.mp3")
                music.play(loops=-1)

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_6):
                music.stop()
                music.unload()
                music.load("assets/sfx/Stray Trash Zone.mp3")
                music.play(loops=-1, start=7)

        keys_pressed = pygame.key.get_pressed()
        if (keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]) and self.alive: 
            self.y_speed -= self.y_acc
            self.fuel -= 1/40
            self.accelerating = True
        if (keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]) and self.alive: 
            self.y_speed += self.y_acc
            self.fuel -= 1/40
            self.accelerating = True
        if (keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]) and self.alive: 
            self.x_speed += self.x_acc
            self.fuel -= 1/40
            self.accelerating = True
        if (keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]) and self.alive: 
            self.x_speed -= self.x_acc
            self.fuel -= 1/40
            self.accelerating = True
        if (keys_pressed[pygame.K_LCTRL]) and self.alive:
            self.x_speed /= 1.5
            self.y_speed /= 1.5
        if (keys_pressed[pygame.K_h]):
            self.fuel = 9002

        # LEGACY CODE

        # if (keys_pressed[pygame.K_r]) and not self.alive:
        #     self.respawn()
        # if (keys_pressed[pygame.K_SPACE]) and self.alive :#and True: #MINE!!!!!!
        #     create_mine()
        # if (keys_pressed[pygame.K_LSHIFT]) and self.alive and (time.time() - last_dash > 2):
        #     self.x_speed += (int(self.x_speed > 0) - 0.5) * 2 * 10
        #     self.y_speed += (int(self.y_speed > 0) - 0.5) * 2 * 10
        #     self.fuel = self.fuel - 3
        #     create_particles("create_subparticles", 20, {"x": self.x, "y": self.y}, 3, 0.12, (100, 100, 255), 36, 5)
        #     self.iframes_left = 20
        #     sfx_dash.play()
        #     self.can_dash = False
        #     score += 25
        #     scoreboard_list.append(["FAST +25", 0])
        #     last_dash = time.time()


    def create_trail(self):
        if self.alive and self.accelerating: ball_trail_list.append({"x": self.x, "y": self.y, "age": 0, "active": True})
        elif self.alive and not self.accelerating: ball_trail_list.append({"x": self.x, "y": self.y, "age": 0, "active": False})
        for ball_trail in ball_trail_list:
            ball_trail["age"] += 1
            if ball_trail["age"] > 9:
                ball_trail_list.pop(ball_trail_list.index(ball_trail))
            if ball_trail["active"]: pygame.draw.circle(window, (max(0, 255 - 24 * ball_trail["age"]), max(0, 255 - 48 * ball_trail["age"]), 0), (ball_trail["x"], ball_trail["y"]), 4 - 0.36 * ball_trail["age"])
            else: pygame.draw.circle(window, (max(0, 31 - 2 * ball_trail["age"]), max(0, 31 - 2 * ball_trail["age"]), 0), (ball_trail["x"], ball_trail["y"]), 4 - 0.36 * ball_trail["age"])

    def die(self):
        if self.Is_Player and score > HighestScore:
            save_game(score)
            pygame.mixer.music.stop()
    
    def update(self):
        self.check_collision()
        if self.Is_Player:
            self.handle_movement()
            self.create_trail()
        self.iframes_left -= 1
        sprite = self.active_sprite if self.accelerating and self.alive else self.inactive_sprite
        window.blit(sprite, (self.x - self.radius, self.y - self.radius))
        self.y_speed += self.gravity
        self.x += self.x_speed
        self.y += self.y_speed
        self.iframes_left -= 1

        if self.fuel <= 0 and self.alive:
            self.die()
            self.alive = False

        if self.alive:
            pass
        else:
            if self.Is_Player:
                window.blit(respawn_text, (WIDTH/2 - 400, HEIGHT/2))


class Enemy(Ball):
    def __init__(self, is_player: bool = False, radius: int = 6, ball_active_sprite: pygame.surface = None, ball_non_active_sprite: pygame.surface = None, initial_location: tuple = (1280 / 2, 720 / 2), fuel: float = 30) -> None:
        super().__init__(is_player, radius, ball_active_sprite, ball_non_active_sprite, initial_location, fuel)

    def update_enemy(self):
        self.update()
        global score, max_enemy_fuel, enemy_list
        self.fuel -= 1/60
        if self.fuel <= 0:
            self.alive = False
            self.accelerating = True
            if self.alive == True:
                create_particles(None, 8, {"x": self.x, "y": self.y}, 4, 0, (20, 52, 100), 50, 5)
                sfx_enemydead.play()
                self.accelerating = False
                self.alive = False
                score += 107
                draw_floatertext(f"+{107}", 20, 2, (playerball.x, playerball.y), (100,100,100))
                scoreboard_list.append(["Slaughtered +107", 0])
        
        if ((abs(playerball.x - self.x) < playerball.radius + self.radius) and (abs(playerball.y - self.y) < playerball.radius + self.radius) and self.alive) and playerball.iframes_left <= 0:
            player_speed = math.sqrt(playerball.x_speed**2 + playerball.y_speed**2)
            if player_speed > 20:
                self.alive = False  
                create_particles(None, 8, {"x": self.x, "y": self.y}, 4, 0, (20, 52, 100), 50, 5)
                sfx_enemydead.play()
                playerball.x_speed = playerball.x_speed - self.x_speed
                playerball.y_speed = playerball.y_speed - self.y_speed
                playerball.fuel += 12.5
                score += 352
                draw_floatertext(f"+{352}", 20, 2, (playerball.x, playerball.y), (100,100,100))
                scoreboard_list.append(["DASHED +352", 0])
            elif playerball.iframes <= 0:
                playerball.fuel = min(playerball.fuel - 4, playerball.fuel / 1.33)
                if playerball.alive:
                    sfx_hit.play()  
                    create_particles(None, 10, {"x": playerball.x, "y": playerball.y}, 4, 0.15, (255, 255 ,255), 60, 5)
                    score -= 91
                    draw_floatertext(f"-{91}", 20, 2, (playerball.x, playerball.y), (100,100,100))
                    scoreboard_list.append(["skill issue -91", 0])

                    playerball.iframes = 20
            else:
                score += 13
                scoreboard_list.append(["Ignored +13", 0])
                playerball.fuel += math.sqrt(2)/3

        if (playerball.x - self.x < 0) and self.alive:
            self.x_speed -= self.x_acc
        elif (self.x - playerball.x < 0) and self.alive: 
            self.x_speed += self.x_acc

        if (playerball.y - self.y < 0) and self.alive:
            self.y_speed -= self.y_acc
        elif (self.y - playerball.y < 0) and self.alive: 
            self.y_speed += self.y_acc
        if (not self.alive) and (abs(self.y_speed) < 0.3) and (abs(self.x_speed) < 0.3):
            enemy_list.pop(enemy_list.index(self))
    

def create_particles(tag, amount, pos, max_speed, fall_acc, color, max_age, radius):
    for _ in range(random.randint(int(amount/2), amount)):
        particle = {"x": pos["x"]+random.randint(-radius, radius), "y": pos["y"]+random.randint(-radius, radius), "x_speed": max_speed * (random.random() - 0.5), "y_speed": max_speed * (random.random() - 0.5), "fall_acc": fall_acc, "age": 0, "tag": tag, "color": color, "max_age": max_age, "radius": radius}
        particle_list.append(particle)

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

def check_goal():
    global score, max_enemy_fuel, max_enemy_timer, playerball
    goal_destroyed["y_speed"] += 0.05
    if goal_destroyed["y"] > HEIGHT-12:
        goal_destroyed["y_speed"] = 0
    goal_destroyed["y"] += goal_destroyed["y_speed"]
    create_particles(None, 1, {"x": goal_destroyed["x"]+12, "y": goal_destroyed["y"]+12}, 0, -0.05, (90, 90, 90), 60, 4)

    if (abs(playerball.x - goal_vars["x"]) < playerball.radius + goal_vars["radius"]) and (abs(playerball.y - goal_vars['y']) < playerball.radius + goal_vars["radius"]):
        create_particles("create_subparticles", 12, {"x": goal_vars["x"], "y": goal_vars["y"]}, 3, 0.07, (255, 255, 0), 50, 6)
        goal_destroyed["x"] = goal_vars["x"] - goal_vars["radius"]
        goal_destroyed["y"] = goal_vars["y"] - goal_vars["radius"]
        goal_destroyed["y_speed"] = 0
        goal_vars["x"] = random.randint(10, WIDTH)
        goal_vars["y"] = random.randint(10, HEIGHT)
        if not playerball.alive: playerball.alive = True; pygame.mixer.music.unpause()
        playerball.fuel = min(60, playerball.fuel + 6.3)
        score += 127
        draw_floatertext(f"+{127}", 20, 2, (playerball.x, playerball.y), (100,100,100))
        sfx_explosion.play()
        max_enemy_fuel *= 1.125
        scoreboard_list.append(["Destroyed +127", 0])
        max_enemy_timer *= 0.925
        max_enemy_timer += 0.2

def create_enemies():
    global enemy_timer, max_enemy_fuel, max_enemy_timer
    enemy_timer -= 1/60
    if enemy_timer <= 0 and playerball.alive:
        sfx_enemyspawn.play()
        enemy_timer = max_enemy_timer
        # enemy_list.append({"x": 500, "y": 500, "x_speed": 0, "y_speed": 0, "x_acc": 0.2, "y_acc": 1/3, "fall_acc": 0.2, "radius": 6, "fuel": round(max_enemy_fuel, 0), "alive": True, "done": False})
        enemy_list.append(Enemy(False, fuel=round(max_enemy_fuel, 0), ball_active_sprite=enemy_sprite, ball_non_active_sprite=enemy_dead_sprite, initial_location=(500,500)))
        create_particles(None, 14, {"x": enemy_list[-1].x,  "y": enemy_list[-1].y}, 4, 0, (200, 0, 0), 50, 5)

def update_enemies():
    create_enemies()
    for enemy in enemy_list:
        enemy.update_enemy()

# all it does is fuck up the sprite
def calc_rotation(velocity: tuple()) -> float:
    """ Input velocity in form of a tuple with 2 elements, x velocity and y velocity.
        Right side positive, upwards negative."""
    velocity_x = velocity[0]
    velocity_y = velocity[1]
    try:
        return (math.atan2(velocity_y, velocity_x) * 180 / math.pi)
    except ZeroDivisionError:
        pass

def create_mine():
    mine["x"] = playerball.x - playerball.radius
    mine["y"] = playerball.y - playerball.radius
    mine["timer"] = 100

def check_mine():
    global score
    mine["timer"] -= 1
    if (mine["timer"] % 20 == 0) and (mine["timer"] > 0):
        sfx_beep.play()
    if mine["timer"] == 0:
        for enemy in enemy_list:
            if ((mine["x"] - enemy.x)**2 + (mine["y"] - enemy.y)**2)**0.5 < 133:
                enemy.alive = False
                enemy.fuel = 0
                score += 411
                scoreboard_list.append(["Blasted +411", 0])
                draw_floatertext("+411", 20, 2, (enemy.x, enemy.y))
        create_particles(None, 1, {"x": mine["x"], "y": mine["y"]}, 0, 0, (255, 180, 0), 10, 133) 
        sfx_mine.play()
        mine["x"] = -500
        mine["y"] = -8000

def check_fps():
    global fps_string
    global last_fps_check_time
    current_time = time.time()
    time_delta = current_time - last_fps_check_time
    fps = 1/time_delta
    fps_list.append(fps)
    if len(fps_list) > 256: fps_list.pop(0)
    fps_string = f"time since last frame: {round(time_delta, 3)} ({round(fps, 1)} fps; {round(np.mean(fps_list), 1)} average; {round(max(fps_list), 1)} max; {round(min(fps_list), 1)} min)"
    last_fps_check_time = current_time

def load_game() -> None:
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

def save_game(HighScore :int) -> None:
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
            Log("Creating save file", "UTLITIY", "SaveGame")
            savefile.close()
    
    with open(f"{savepath}/save.balls", "wb") as savefile:
        Log("Saving to save file", "UTILITY", "SaveGame")
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
ball_active_sprite = pygame.image.load("assets/sprites/ball_active.png")
goal_sprite        = pygame.image.load("assets/sprites/goal.png")
enemy_sprite       = pygame.image.load("assets/sprites/enemy.png")
enemy_dead_sprite  = pygame.image.load("assets/sprites/enemy_dead.png")
destroyed_goal_sprite = pygame.image.load("assets/sprites/goal_destroyed.png")
mine_sprite        = pygame.image.load("assets/sprites/mine.png")
fish_sprite        = pygame.image.load("assets/sprites/fish.png")

# Background, no shit sherlock
bgscale = 1 # How big the background is, no shit sherlock
bgimage = pygame.transform.scale_by(pygame.image.load("assets/sprites/background.png"), bgscale)

#ball_vars = {"x": WIDTH/2, "y": HEIGHT/2, "fuel": 30, "x_speed": 0, "y_speed": 0, "x_acc": 1/3, "y_acc": 0.75, "self_gravity": 0.2, "alive": True, "radius": 6, "accelerating": False, "iframes_left": 0}
goal_vars = {"x": random.randint(10, HEIGHT-10), "y": random.randint(10, HEIGHT-10), "radius": 12}
fuel_consumption = 1/240
can_dash = True
enemy_list = []
global enemy_timer; enemy_timer = 1             # Why are these marked as global if they are already global | it works and therefore im not touching it
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
pygame.mixer.music.load("assets/sfx/Lethal company boombox song 5.mp3")
pygame.mixer.music.set_volume(2.0)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 18)

running = True
load_game()
Dead = False
pygame.mixer.music.play(loops=-1)

playerball = Ball(True, 6, ball_active_sprite, ball_sprite, (WIDTH/2, HEIGHT/2))

while running:
    events = pygame.event.get()
    playerball.PygameEvents = events
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            break

    # window.fill((0, 0, 0)) # Do we still need this? Lmfao no but let's keep this line for funni

    # Blit background, no shit sherlock
    window.blit(bgimage, (0,0))

    playerball.accelerating = False
    playerball.fuel -= fuel_consumption
    if playerball.fuel <= 0: 
        playerball.alive = False
        window.blit(respawn_text, (WIDTH/2 - 400, HEIGHT/2))
        if score > HighestScore and not Dead:
            save_game(score)
        pygame.mixer.music.pause()
        Dead = True
    else: playerball.alive = True

    playerball.iframes -= 1
    check_fps()
    pygame.draw.circle(window, (24, 16, 0), (mine["x"], mine["y"]), 100)
    check_goal()
    check_mine()
    update_enemies()
    update_floatertext()
    update_scoreboard()

    # High score no shit sherlock
    highscoretext = font.render(f"High score: {HighestScore}", False, (100,100,100))
    window.blit(pygame.transform.scale_by(highscoretext, 1.2), (WIDTH-230, 50))

    # Simple scoreboard no shit sherlock
    scoretext = font.render(f"Score: {score}", False, (100,100,100))
    window.blit(pygame.transform.scale_by(scoretext, 1.2), (WIDTH-230, 70))

    # Frame rate information no shit sherlock
    fpstext = font.render(fps_string, False, (255,255,255))
    window.blit(fpstext, (300, 10))

    # Devboi do not fucking remove this loop or i will beat your skull into dust with a lead pipe
    # I will. <- this line was written by a person with massive skill issues
    #              ^ That line was written by a person with even bigger skill issues
    #                   f^ i REALLY hate how this person writes python code
    strings = [
         "║║        ║ ╚═╗       ║",
         '║║[ YELLOW IS FUEL ]  ║',
         '║║ [ RED ARE THREAT ]═╝',
         '║╚══[ GOAL:  SURVIVE ]',
         '║ ',
        f'╠═[ x ]═[ {int(playerball.x)} ]',
        f'╠═[ y ]═[ {int(playerball.y)} ]',
        f'╠═[ f ]═[ {max(round(playerball.fuel, 1), 0)} ] ← !!',
        f'╠═[ X ]═[ {round(playerball.x_speed, 2)} ]',
        f'╠═[ Y ]═[ {round(playerball.y_speed, 2)} ]',
        f'╠═[ i ]═[ {max(playerball.iframes, 0)} ]',
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

    particle_update()

    window.blit(goal_sprite, (goal_vars["x"] - goal_vars["radius"], goal_vars["y"] - goal_vars["radius"]))
    window.blit(mine_sprite, (mine["x"]-5, mine["y"]-5))
    
    playerball.update()

    frame += 1
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

"""
TODO add kill combo bonuses
TODO add a bossfight (fish boss real)
TODO improve the visual effects
TODO fix game freezing shortly after dying (reason unknown)
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
DONE add sfx and bgm
"""
# j <- literally the only instance of this letter in the entire code :skull: