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
from pathlib import Path
pygame.init()
pygame.mixer.init()
music = pygame.mixer.music
sound = pygame.mixer.Sound

WIDTH, HEIGHT = 1024, 768

class Ball:
    def __init__(self, is_player: bool = False, radius: int = 6, ball_active_sprite: pygame.surface = None, ball_non_active_sprite: pygame.surface = None, initial_location: tuple = (1280/2, 720/2), fuel: float = 30, iframes: int = 0, align_with_velocity: bool = False):
        self.x = initial_location[0]
        self.y = initial_location[1]
        self.PygameEvents = []
        self.iframes_left = 0
        self.gravity = 0.4
        self.total_vel = 0
        self.y_acc = 1
        self.x_acc = 0.4
        self.x_vel = 0
        self.y_vel = 0
        self.accelerating = True
        self.can_dash = True
        self.alive = True
        self.align_with_velocity = align_with_velocity
        self.inactive_sprite = ball_non_active_sprite
        self.active_sprite = ball_active_sprite
        self.is_player = is_player
        self.iframes = iframes
        self.radius = radius
        self.fuel = fuel
        
    def check_collision(self):
        # right border
        if self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.x_vel *= -0.6
            if self.x_vel < -0.4 and self.is_player:
                create_particles(None, 4, {"x": self.x, "y": self.y}, 3, 0.12, (255, 255, 255), 36, 5)
                sfx_bounce.play()

        # left border
        if self.x < self.radius:
            self.x = self.radius
            self.x_vel *= -0.6
            if self.x_vel > 0.4 and self.is_player:
                create_particles(None, 4, {"x": self.x, "y": self.y}, 3, 0.12, (255, 255, 255), 36, 5)
                sfx_bounce.play()

        # top border
        if self.y < self.radius:
            self.y = self.radius
            self.y_vel *= -0.6
            if self.y_vel > 0.4 and self.is_player:
                create_particles(None, 4, {"x": self.x, "y": self.y}, 3, 0.12, (255, 255, 255), 36, 5)
                sfx_bounce.play()

        # bottom border
        if self.y > HEIGHT - self.radius:
            self.y = HEIGHT - self.radius
            self.y_vel *= -0.6
            if self.x_vel > 0:
                self.x_vel -= 0.01
            if self.x_vel < 0:
                self.x_vel += 0.01
            if self.y_vel < -0.4 and self.is_player:
                create_particles(None, 4, {"x": self.x, "y": self.y}, 3, 0.12, (255, 255, 255), 36, 5)
                sfx_bounce.play()

    def respawn(self):
        global score, enemy_list, max_enemy_timer
        enemy_list = []
        max_enemy_timer = 3
        self.y = HEIGHT/2
        self.x = WIDTH/2
        self.fuel = 30
        self.x_vel = 0
        self.y_vel = 0
        score = 0
        self.alive = True
        load_game()

    def handle_movement(self):
        global score, last_dash, user_fps, paused

        for event in self.PygameEvents:
            if event.type == pygame.KEYDOWN and event.key == (pygame.K_LSHIFT) and self.alive:
                self.total_vel = math.sqrt(self.x_vel**2 + self.y_vel**2)
                self.x_vel += 20 * (self.x_vel / self.total_vel)
                self.y_vel += 20 * (self.y_vel / self.total_vel)
                self.fuel -= 2
                create_particles("create_subparticles", 15, {"x": self.x, "y": self.y}, 13, 0.03, (100, 100, 255), 8, 5)
                self.iframes = max(self.iframes + 8, 8)
                sfx_dash.play()
                score += 25
                scoreboard_list.append(["FAST +25", 0, (80, 80, 130)])
                floating_text_list.append({"text": "+25", "size": 20, "duration": frame + 120, "position": (playerball.x, playerball.y), "color": (80, 80, 130)})
            
            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_SPACE) and self.alive and mine["timer"] < -45:
                create_mine()
                self.fuel -= 3
        
            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_r) and not self.alive:
                self.respawn()

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_g) and self.alive:
                grenades_list.append({"x": self.x, "y": self.y, "x_vel": self.x_vel * 0.4, "y_vel": self.y_vel * 0.4, "y_acc": 0.1, "age": random.randint(-90, -40)})
                grenades_list.append({"x": self.x, "y": self.y, "x_vel": self.x_vel * 0.6, "y_vel": self.y_vel * 0.6, "y_acc": 0.1, "age": random.randint(-90, -40)})
                self.fuel -= 1.5
                sfx_grenade_spawn.play()

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_EQUALS):
                user_fps += 6

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_MINUS):
                user_fps -= 6

            # music switcher (very cool) #TODO add new musics some of these fuckign suck lamo
            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_1):
                music.unload()
                music.load("assets/sfx/Lethal company boombox song 5.mp3")
                floating_text_list.append({"text": "Now playing Lethal Company Boombox song 5", "size": 20, "duration": frame + 120, "position": (50, HEIGHT - 50), "color": (255,255,255)})
                music.play(loops=-1)
            
            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_2):
                music.unload()
                music.load("assets/sfx/Electro-Light - Symbolism [NCS Release].mp3")
                floating_text_list.append({"text": "Now playing Turi ip ip ip", "size": 20, "duration": frame + 120, "position": (50, HEIGHT - 50), "color": (255,255,255)})
                music.play(loops=-1, start=3)

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_3):
                music.unload()
                music.load("assets/sfx/HL2 Apprehension and Evasion.mp3")
                floating_text_list.append({"text": "Now playing Half Life 2 Apprehension and Evasion", "size": 20, "duration": frame + 120, "position": (50, HEIGHT - 50), "color": (255,255,255)})
                music.play(loops=-1, start=10)

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_4):
                music.unload()
                music.load("assets/sfx/HL Credits Closing Theme.mp3")
                floating_text_list.append({"text": "Now playing Half Life Closing Theme", "size": 20, "duration": frame + 120, "position": (50, HEIGHT - 50), "color": (255,255,255)})
                music.play(loops=-1)

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_5):
                music.unload()
                music.load("assets/sfx/Stray Error-22.mp3")
                floating_text_list.append({"text": "Now playing Stray Error-22", "size": 20, "duration": frame + 120, "position": (50, HEIGHT - 50), "color": (255,255,255)})
                music.play(loops=-1)

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_6):
                music.unload()
                music.load("assets/sfx/Stray Error-22.mp3")
                floating_text_list.append({"text": "Now playing Stray Trash Zone", "size": 20, "duration": frame + 120, "position": (50, HEIGHT - 50), "color": (255,255,255)})
                music.play(loops=-1, start=7)

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_7):
                music.unload()
                music.load("assets/sfx/GD Stay Inside Me.mp3")
                floating_text_list.append({"text": "Now playing Geometry Dash Stay inside me", "size": 20, "duration": frame + 120, "position": (50, HEIGHT - 50), "color": (255,255,255)})
                music.play(loops=-1)

            elif event.type == pygame.KEYDOWN and event.key == (pygame.K_0):
                cycle_user_music()

        keys_pressed = pygame.key.get_pressed()
        if (keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]) and self.alive: 
            self.y_vel -= self.y_acc
            self.fuel -= 1/40
            self.accelerating = True

        if (keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]) and self.alive: 
            self.y_vel += self.y_acc
            self.fuel -= 1/40
            self.accelerating = True

        if (keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]) and self.alive: 
            self.x_vel += self.x_acc
            self.fuel -= 1/40
            self.accelerating = True

        if (keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]) and self.alive: 
            self.x_vel -= self.x_acc
            self.fuel -= 1/40
            self.accelerating = True

        if (keys_pressed[pygame.K_LCTRL]) and self.alive:
            self.x_vel /= 1.5
            self.y_vel /= 1.5

        if (keys_pressed[pygame.K_h]):
            self.fuel = 2**31-1

        self.total_vel = math.sqrt(self.x_vel**2 + self.y_vel**2)

    def create_trail(self):
        if self.alive and self.accelerating: ball_trail_list.append({"x": self.x, "y": self.y, "age": 0, "active": True})
        elif self.alive and not self.accelerating: ball_trail_list.append({"x": self.x, "y": self.y, "age": 0, "active": False})
        for ball_trail in ball_trail_list:
            ball_trail["age"] += 1
            if ball_trail["age"] > 9:
                ball_trail_list.pop(ball_trail_list.index(ball_trail))

            if sprite_sheet_index == 2:
                if ball_trail["active"]: pygame.draw.circle(window, (0, max(0, 255 - 48 * ball_trail["age"]), max(0, 255 - 24 * ball_trail["age"])), (ball_trail["x"], ball_trail["y"]), 4 - 0.36 * ball_trail["age"])
                else: pygame.draw.circle(window, (0, max(0, 31 - 2 * ball_trail["age"]), max(0, 255 - 24 * ball_trail["age"])), (ball_trail["x"], ball_trail["y"]), 4 - 0.36 * ball_trail["age"])
            
            else:
                if ball_trail["active"]: pygame.draw.circle(window, (max(0, 255 - 24 * ball_trail["age"]), max(0, 255 - 48 * ball_trail["age"]), 0), (ball_trail["x"], ball_trail["y"]), 4 - 0.36 * ball_trail["age"])
                else: pygame.draw.circle(window, (max(0, 31 - 2 * ball_trail["age"]), max(0, 31 - 2 * ball_trail["age"]), 0), (ball_trail["x"], ball_trail["y"]), 4 - 0.36 * ball_trail["age"])

    def die(self):
        if self.is_player and score > highest_score:
            save_game(score)
            pygame.mixer.music.stop()
    
    def update(self):
        self.fuel += 0.01
        self.check_collision()
        if self.is_player:
            self.handle_movement()
            self.create_trail()
        self.iframes_left -= 1
        sprite = self.active_sprite if self.accelerating and self.alive else self.inactive_sprite
        if self.align_with_velocity:
            window.blit(pygame.transform.rotate(sprite, calc_rotation([self.x_vel, self.y_vel])+90), (self.x - self.radius, self.y - self.radius))
        else:
            window.blit(sprite, (self.x - self.radius, self.y - self.radius))
        self.y_vel += self.gravity
        self.x += self.x_vel
        self.y += self.y_vel
        self.iframes_left -= 1

        if self.fuel <= 0 and self.alive:
            self.die()
            self.alive = False

        if self.alive:
            pass
        else:
            if self.is_player:
                window.blit(respawn_text, (WIDTH/2 - 400, HEIGHT/2))


class Enemy(Ball):
    def __init__(self, is_player: bool = False, radius: int = 6, ball_active_sprite: pygame.surface = None, ball_non_active_sprite: pygame.surface = None, initial_location: tuple = (1280 / 2, 720 / 2), fuel: float = 30, speed_multiplier: float=1, align_with_velocity:bool = False, tag: str="enemy") -> None:
        super().__init__(is_player, radius, ball_active_sprite, ball_non_active_sprite, initial_location, fuel, align_with_velocity=align_with_velocity)
        self.natural_acc = speed_multiplier
        self.tag = tag

    def update_enemy(self):
        global score, enemy_list, last_kill_time, combo_timeout, combo_multiplier, max_enemy_timer
        self.update()
        
        if ((abs(playerball.x - self.x) < playerball.radius + self.radius) and (abs(playerball.y - self.y) < playerball.radius + self.radius) and self.alive) and playerball.iframes_left <= 0:
            enemy_vel = math.sqrt(self.x_vel**2 + self.y_vel**2)
            vel_diff = abs(abs(playerball.total_vel) - abs(enemy_vel))
            if vel_diff > 20 and abs(playerball.total_vel) >= abs(enemy_vel):
                last_kill_time = time.time()
                self.alive = False  
                create_particles(None, 8, {"x": self.x, "y": self.y}, 4, 0, (20, 52, 100), 50, 5)
                sfx_enemydead.play()
                self.x_vel = playerball.x_vel
                self.y_vel = playerball.y_vel
                playerball.fuel += 12.5
                score += 399
                enemy_killed(self.tag)
                floating_text_list.append({"text": "+399", "size": 20, "duration": frame + 120, "position": (playerball.x, playerball.y), "color": (127, 60, 30)})
                scoreboard_list.append(["DASHED +399", 0, (127, 60, 30)])

                if self.tag == "goal":
                    playerball.fuel += 16.3
                    self.x_vel /= 4
                    self.y_vel /= 4
                    create_particles("None", 20, {"x": self.x, "y": self.y}, 6, 0.03, (255, 255, 0), 50, 6)
                    create_particles("create_subparticles", 7, {"x": self.x, "y": self.y}, 12, 0.02, (255, 255, 0), 20, 6)
                    scoreboard_list.append(["Refuel +242", 0, (180, 180, 0)])
                    random.choice(sfx_explosion_list).play()
                    max_enemy_timer *= 0.9

                # Combo bombo  NEEDS FIXING
                if time.time() - last_kill_time <= combo_timeout:
                    combo_multiplier += 1
                    if combo_multiplier >= 2:
                        scoreboard_list.append([f"Kill x{combo_multiplier} {250*combo_multiplier*1.2**combo_multiplier}", 0, (140, 60, 140)])
                        score += 250*combo_multiplier*1.2**combo_multiplier
                    
            elif playerball.iframes <= 0:
                playerball.fuel = min(playerball.fuel - 4, playerball.fuel / 1.33)
                if playerball.alive:
                    sfx_hit.play()  
                    create_particles(None, 10, {"x": playerball.x, "y": playerball.y}, 4, 0.15, (255, 255, 255), 60, 5)
                    score -= 91
                    floating_text_list.append({"text": "-91", "size": 20, "duration": frame + 120, "position": (playerball.x, playerball.y), "color": (100, 100, 100)})
                    scoreboard_list.append(["skill issue -91", 0, (50, 50, 50)])

                    playerball.iframes = 20

        if (playerball.x < self.x) and self.alive:
            self.x_vel -= self.x_acc * self.natural_acc

        elif (playerball.x > self.x) and self.alive: 
            self.x_vel += self.x_acc * self.natural_acc

        if (playerball.y < self.y) and self.alive:
            self.y_vel -= self.y_acc * self.natural_acc

        elif (playerball.y > self.y) and self.alive: 
            self.y_vel += self.y_acc * self.natural_acc

        if (not self.alive) and (abs(self.y_vel) < 0.3) and (abs(self.x_vel) < 0.3):
            enemy_list.pop(enemy_list.index(self))
    

# thanks to python.org for the code
class spritesheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename)
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size)
        image.blit(self.sheet, (0, 0), rect)
        image.convert_alpha()
        image.set_colorkey((0, 0, 0))
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


def create_particles(tag, amount, pos, max_vel, fall_acc, color, max_age, radius):
    for _ in range(random.randint(math.ceil(amount/2), amount)):
        particle = {"x": pos["x"]+random.randint(-radius, radius), "y": pos["y"]+random.randint(-radius, radius), "x_vel": max_vel * (random.random() - 0.5), "y_vel": max_vel * (random.random() - 0.5), "fall_acc": fall_acc, "age": 0, "tag": tag, "color": color, "max_age": max_age, "radius": radius}
        particle_list.append(particle)

def log(text: str, category: str, location: str):
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

def update_floatertext():
    i = 0
    for text in floating_text_list:
        if frame > text["duration"]: 
            floating_text_list.pop(i)
        else:
            fontrender = pygame.font.Font("assets/VCR_OSD_MONO_1.001.ttf", text["size"])
            rend = fontrender.render(text["text"], False, text["color"])
            floating_text_list[i] = text

            window.blit(rend, text["position"])
        i+=1

def particle_update():
    i = 0
    for particle in particle_list:
        particle["age"] += int(random.random() < 0.80)
        if particle["age"] > particle["max_age"]:
            particle_list.pop(i)
    
        particle["y_vel"] += particle["fall_acc"]
        particle["x"] += particle["x_vel"]
        particle["y"] += particle["y_vel"]

        if (particle["tag"] == "create_subparticles"):
            particle_list.append({"x": particle["x"], "y": particle["y"], "x_vel": 0, "y_vel": 0, "fall_acc": 0, "age": int(particle["age"]/2), "tag": None, "color": particle["color"], "max_age": particle["max_age"]*1.25, "radius": particle["radius"]})

        pygame.draw.circle(window, (max(int(particle["color"][0] - particle["color"][0] * (particle["age"] / particle["max_age"])), 0), 
                                    max(int(particle["color"][1] - particle["color"][1] * (particle["age"] / particle["max_age"] * 1.5)), 0), 
                                    max(int(particle["color"][2] - particle["color"][2] * (particle["age"] / particle["max_age"] * 2.0)), 0)),
                                    (particle["x"], particle["y"]), particle["radius"] - particle["radius"] * (particle["age"] / particle["max_age"]))
        i += 1

def create_enemies():
    global enemy_timer, max_enemy_timer
    enemy_timer -= 1/60
    if enemy_timer <= 0 and playerball.alive:
        sfx_enemyspawn.play()
        enemy_timer = max_enemy_timer
        # enemy_list.append({"x": 500, "y": 500, "x_vel": 0, "y_vel": 0, "x_acc": 0.2, "y_acc": 1/3, "fall_acc": 0.2, "radius": 6, "fuel": round(max_enemy_fuel, 0), "alive": True, "done": False})
        if random.random() > 0.3:
            enemy_list.append(Enemy(False, 6, enemy_sprite, enemy_dead_sprite, (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 9001, 1, False))
        else:
            enemy_list.append(Enemy(False, 12, goal_sprite, destroyed_goal_sprite, (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 9001, 0.4, False, "goal"))
        
        create_particles(None, 14, {"x": enemy_list[-1].x,  "y": enemy_list[-1].y}, 4, 0, (200, 0, 0), 50, 5)

def update_enemies():
    create_enemies()
    for enemy in enemy_list:
        enemy.update_enemy()

def calc_rotation(velocity: tuple) -> float:
    # Input velocity in form of a tuple with 2 elements, x velocity and y velocity
    # Right side positive, upwards negative
    try:
        return ((math.atan2(velocity[0], velocity[1]))* 180 / math.pi)
    except ZeroDivisionError:
        return 0

def create_mine():
    mine["x"] = playerball.x - playerball.radius
    mine["y"] = playerball.y - playerball.radius
    mine["timer"] = 80
    sfx_mine_spawn.play()

def check_mine():
    global score, last_kill_time, combo_timeout, combo_multiplier
    mine["timer"] -= 1
    if (mine["timer"] % 20 == 0) and (mine["timer"] > 0):
        sfx_beep.play()
    if mine["timer"] == 0:
        for enemy in enemy_list:
            if (((mine["x"] - enemy.x)**2 + (mine["y"] - enemy.y)**2)**0.5 < 133) and enemy.alive:
                enemy.alive = False
                enemy.fuel = 0
                score += 411
                enemy_killed(enemy.tag)
                scoreboard_list.append(["Blasted +411", 0, (255, 255, 0)])
                
                # Combo bombo  
                if time.time() - last_kill_time <= combo_timeout:
                    combo_multiplier += 1
                    if combo_multiplier >= 2:
                        scoreboard_list.append([f"Kill x{combo_multiplier} {250*combo_multiplier*1.2*combo_multiplier}", 0, (140, 80, 140)])
                        score += 250*combo_multiplier*1.2**combo_multiplier
                else:
                    combo_multiplier = 1

                floating_text_list.append({"text": "+411", "size": 20, "duration": frame + 120, "position": (enemy.x, enemy.y), "color": (255, 255, 0)})
        create_particles(None, 1, {"x": mine["x"], "y": mine["y"]}, 0, 0, (255, 180, 0), 5, 166) 
        random.choice(sfx_mine_list).play()
        mine["x"] = -500
        mine["y"] = -8000

def check_fps():
    global fps_string, last_fps_check_time
    current_time = time.time()
    time_delta = current_time - last_fps_check_time
    fps = 1/time_delta
    fps_list.append(fps)
    if len(fps_list) > 256: fps_list.pop(0)
    fps_string = f"{round(time_delta*1000, 1)} ms ({round(fps, 1)} ups; {round(np.mean(fps_list), 1)} avg; {round(max(fps_list), 1)} max; {round(min(fps_list), 1)} min; {user_fps} set max)"
    last_fps_check_time = current_time

def load_game() -> None:
    try:
        with open(f"{savepath}/save.balls", "rb") as savefile:
            try:
                global highest_score
                savedata = pickle.load(savefile)

                highest_score = savedata["playerdata"]["HighScore"]
                
                log ("Loading data from save file", "UTILITY", "LoadGame")
            except Exception as e:
                log (f"{traceback.format_exc}", "ERROR", "LoadGame")
                
    except FileNotFoundError:
        log ("No save file found", "WARNING", "LoadGame")

def save_game(HighScore: int) -> None:
    try:
        with open(f"{savepath}/save.balls", "rb") as savefile:
            savefile.close()
    except FileNotFoundError:
        log("Save file does not exist.", "WARNING", "SaveGame")
        try:
            os.mkdir(savepath)
            log("Creating save folder", "UTLITIY", "SaveGame")
        except FileExistsError:
            log("Save folder exists, but the file does not.", "WARNING", "SaveGame")

        with open(f"{savepath}/save.balls", "+wb") as savefile:
            log("Creating save file", "UTLITIY", "SaveGame")
            savefile.close()
    
    with open(f"{savepath}/save.balls", "wb") as savefile:
        log("Saving to save file", "UTILITY", "SaveGame")
        savedata = {}
        savedata["playerdata"] = {"HighScore" : HighScore}
        pickle.dump(savedata, savefile)

def update_scoreboard():
    i = 0
    for item in scoreboard_list: 
        item[1] += 1
        if item[1] > 120:
            scoreboard_list.pop(i)

        text = default_font.render(item[0], False, item[2])
        window.blit(text, (WIDTH-230, 95 + 18*i))
        i += 1

def cycle_user_music():
    global musicindex, music_files
    try:
        if len(music_files) > 0:
            if musicindex > len(music_files) -1:
                musicindex = 0
            file = os.path.join(music_path, music_files[musicindex])
            music.unload()
            music.load(file)
            display_text = f"Now playing {music_files[musicindex]}"
            music.play(loops=-1, start=7)
            musicindex +=1
        else:
            display_text = "No music files found."
    except:

        display_text = "Couldn't find music in the music directory"
    floating_text_list.append({"text": display_text, "size": 20, "duration": frame + 120, "position": (WIDTH/2 - len(display_text)*6, HEIGHT - 50), "color": (255,255,255)})
    
def handle_grenades():
    global score
    i = 0
    for grenade in grenades_list:
        grenade["y_vel"] += grenade["y_acc"]
        grenade["x"] += grenade["x_vel"] 
        grenade["y"] += grenade["y_vel"]

        if grenade["x"] > WIDTH:
            grenade["x_vel"] *= -1
            grenade["x"] = WIDTH-4

        if grenade["x"] < 0:
            grenade["x_vel"] *= -1
            grenade["x"] = 4

        if grenade["y"] > HEIGHT:
            grenade["y_vel"] *= -1
            grenade["y"] = HEIGHT-4

        if grenade["y"] < 0:
            grenade["y_vel"] *= -1
            grenade["y"] = 4

        grenade["age"] += 1
        if grenade["age"] >= 0:
            grenades_list.pop(i)
            create_particles(None, 1, {"x": grenade["x"], "y": grenade["y"]}, 0, 0, (255, 180, 0), 5, 40) 
            random.choice(sfx_mine_list).play()
            continue
        for enemy in enemy_list:
            if (((grenade["x"] - enemy.x)**2 + (grenade["y"] - enemy.y)**2)**0.5 < 30) and grenade["age"] > -25 and enemy.alive:
                create_particles(None, 1, {"x": grenade["x"], "y": grenade["y"]}, 0, 0, (255, 180, 0), 5, 40)
                grenades_list.pop(i) 
                enemy.alive = False
                enemy.fuel = 0
                score += 311
                enemy_killed(enemy.tag)
                scoreboard_list.append(["Bombed +911", 0, (255, 100, 0)])
                random.choice(sfx_mine_list).play()
        i += 1

        window.blit(pygame.transform.rotate(grenade_sprite, calc_rotation([grenade["x_vel"], grenade["y_vel"]])-180), (grenade["x"], grenade["y"]))

def enemy_killed(enemy_tag: str):
    global kill_count, enemy_list, floating_text_list, scoreboard_list, score
    if enemy_tag == "fishy":
        scoreboard_list.append(["Killed Boss +1000", -100, (255, 255, 0)])
        score += 1000
    else:
        pass
    kill_count +=1
    if kill_count % (7 + kill_count//7) == 0:
        fish_boss = Enemy(False, 200, fish_sprite, dead_fish_sprite, fuel=100*(1+ kill_count/7)*30, initial_location=(WIDTH//2, HEIGHT//2), speed_multiplier=0.66, align_with_velocity=True, tag="fishy")
        floating_text_list.append({"text": "BOSS FIGHT! FISH BOSS!", "size": 80, "duration": frame + 180, "position": (WIDTH//2 - 500, HEIGHT//2 - 100), "color": (100, 100, 100)})
        enemy_list.append(fish_boss)



window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption(random.choice(["I wokup inanew bugatti", "Don't forget to tell xenonmite_ his art is shid", "Racist baller", "⚪🟡🔴", "Devboi please do not use pascal case", "If your high score is less than 20000, it's a skill issue"]))

default_bg       = pygame.image.load("assets/sprites/background.png")
dead_fish_sprite = pygame.image.load("assets/sprites/fish_dead.png")
troll_bg         = pygame.image.load("assets/sprites/troll.png")
minecraft_bg     = pygame.image.load("assets/sprites/wall.png")
fish_sprite      = pygame.image.load("assets/sprites/fish.png")

ss = spritesheet("assets/sprites/spritesheet_0.png")
ball_sprite        = ss.image_at((0, 0, 12, 12))
ball_active_sprite = ss.image_at((12, 0, 12, 12))
goal_sprite        = ss.image_at((0, 12, 24, 24))
destroyed_goal_sprite = ss.image_at((24, 10, 24, 24))
enemy_sprite       = ss.image_at((24, 0, 10, 10))
enemy_dead_sprite  = ss.image_at((34, 0, 10, 10))
mine_sprite        = ss.image_at((44, 0, 10, 10))
grenade_sprite     = ss.image_at((48, 10, 8, 12))
sprite_sheet_index = 0

goal_destroyed = {"x": -500, "y": -8000, "y_vel": 0}
mine = {"x": -500, "y": -8000, "timer": -1}

floating_text_list = []   
ball_trail_list = []
scoreboard_list = []
particle_list = []
grenades_list = []
enemy_list = []
fps_list = []

show_floating_text_for = 0
last_fps_check_time = 0
fuel_consumption = 1/240
combo_multiplier = 1
max_enemy_timer = 3
last_kill_time = 0
combo_timeout = 3
highest_score = 0
enemy_timer = 1             # Why are these marked as global if they are already global | it works and therefore im not touching it | Bruh | nvm i touched it; do we remove this line or do we keep it for history
kill_count = 0
musicindex = 0
last_dash = 0
user_fps = 60
score = 0
frame = 0

fps_string = ""
savepath = "Saves"

can_dash = True
paused = False

music_path = str(Path.home() / "Music")
music_files = next(os.walk(music_path), (None, None, []))[2]
music_files = [file for file in music_files if file.split(".")[-1] in ["mp3", "ogg", "wav"]]

death_text_font = pygame.font.Font("assets/VCR_OSD_MONO_1.001.ttf", 50)
respawn_text = death_text_font.render("Dead. Press 'R' to respawn", False, (100, 100, 100))

# Initialize audios
sfx_mine_list  = [sound("assets/sfx/mine0.wav"), sound("assets/sfx/mine1.wav"), sound("assets/sfx/mine2.wav"), sound("assets/sfx/mine3.wav"), sound("assets/sfx/mine4.wav")]
sfx_explosion_list = [sound("assets/sfx/explosion0.wav"), sound("assets/sfx/explosion1.wav")]

sfx_grenade_spawn = sound("assets/sfx/grenade_spawn.wav")
sfx_spongebob     = sound("assets/sfx/im-spongebob.mp3")
sfx_enemyspawn    = sound("assets/sfx/enemyspawn.wav")
sfx_mine_spawn    = sound("assets/sfx/mine_spawn.wav")
sfx_enemydead     = sound("assets/sfx/enemydead.wav")
sfx_quickfuel     = sound("assets/sfx/quickfuel.wav")
sfx_revive        = sound("assets/sfx/revive.mp3")
sfx_bounce        = sound("assets/sfx/bounce.wav")
sfx_dash          = sound("assets/sfx/dash.wav")
sfx_beep          = sound("assets/sfx/beep.wav")
sfx_hit           = sound("assets/sfx/hit.wav")

pygame.mixer.music.load("assets/sfx/GD Stay Inside Me.mp3")
pygame.mixer.music.play(loops=-1)

clock = pygame.time.Clock()
default_font = pygame.font.Font("assets/VCR_OSD_MONO_1.001.ttf", 20)
running = True

load_game()

playerball = Ball(True, 6, ball_active_sprite, ball_sprite, (WIDTH/2, HEIGHT/2))

while running:
    events = pygame.event.get()
    playerball.PygameEvents = events
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            break

        elif event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            WIDTH = window.get_width()
            HEIGHT = window.get_height()

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            paused = not paused
            fontrender = pygame.font.Font("assets/VCR_OSD_MONO_1.001.ttf", 80)
            rend = fontrender.render("[ PAUSED ]", False, (50, 50, 50))
            window.blit(rend, (WIDTH / 2 - rend.get_width() / 2, HEIGHT / 2 - rend.get_height() / 2))

        elif event.type == pygame.KEYDOWN and event.key == (pygame.K_t):
            sfx_spongebob.play()
            sprite_sheet_index = 1 if sprite_sheet_index == 0 else 2 if sprite_sheet_index == 1 else 3 if sprite_sheet_index == 2 else 0
            ss = spritesheet(f"assets/sprites/spritesheet_{sprite_sheet_index}.png")

            ball_sprite           = ss.image_at((0, 0, 12, 12))
            ball_active_sprite    = ss.image_at((12, 0, 12, 12))
            goal_sprite           = ss.image_at((0, 12, 24, 24))
            destroyed_goal_sprite = ss.image_at((24, 10, 24, 24))
            enemy_sprite          = ss.image_at((24, 0, 10, 10))
            enemy_dead_sprite     = ss.image_at((34, 0, 10, 10))
            mine_sprite           = ss.image_at((44, 0, 10, 10))
            grenade_sprite        = ss.image_at((48, 10, 8, 12))

            playerball.active_sprite = ball_active_sprite
            playerball.inactive_sprite = ball_sprite

            for enemy in enemy_list:
                enemy.active_sprite = enemy_sprite
                enemy.inactive_sprite = enemy_dead_sprite

    # window.fill((0, 0, 0)) # Do we still need this? Lmfao no but let's keep this line for funni

    if not paused:
        # Blit background, no shit sherlock
        match sprite_sheet_index:
            case 2: window.blit(minecraft_bg, (0, 0))
            case 3: window.blit(troll_bg, (0, 0))
            case _: window.blit(default_bg, (0, 0))

        playerball.accelerating = False
        playerball.fuel -= fuel_consumption

        if time.time() - last_kill_time > combo_timeout:
            combo_multiplier = 1

        playerball.iframes -= 1
        pygame.draw.circle(window, (24, 16, 0), (mine["x"], mine["y"]), 100)
        check_fps()
        check_mine()
        playerball.update()
        handle_grenades()
        update_enemies()
        update_scoreboard()
        update_floatertext()
        particle_update()

        highscore_text = default_font.render(f"High score: {int(highest_score)}", False, (100,100,100))
        window.blit(highscore_text, (min(WIDTH - highscore_text.get_width(), WIDTH - 230), 50))

        score_text = default_font.render(f"Score: {int(score)}", False, (100,100,100))
        window.blit(score_text, (min(WIDTH - score_text.get_width(), WIDTH - 230), 70))

        fps_text = default_font.render(fps_string, False, (255,255,255))
        window.blit(fps_text, (WIDTH/2 - fps_text.get_width()/2, 5))

        # Devboi do not fucking remove this loop or i will beat your skull into dust with a lead pipe
        # I will. <- this line was written by a person with massive skill issues
        #               ^ That line was written by a person with even bigger skill issues
        #                   ^ i REALLY hate how this person writes python code
        #                       ^ I will continue using PascalCase cry about it lol xd
        #                           ^ i will cancel you on twitter and youtube
        #                               ^ I will change all variable names to 1 letter names
        #                                   ^ you are no longer allowed to make commits /j (or is it (it's not))

        strings = [
             "||        | L,        |",
             '||[ YELLOW IS FUEL ]  |',
             '|| [ RED ARE THREAT ]=J',
             '|  L==[ GOAL:  SURVIVE ]',
             '| ',
            f'|=[ x ]=[ {int(playerball.x)} ]',
            f'|=[ y ]=[ {int(playerball.y)} ]',
            f'|=[ k ]=[ {kill_count} ]',
            f'|=[ X ]=[ {round(playerball.x_vel, 2)} ]',
            f'|=[ Y ]=[ {round(playerball.y_vel, 2)} ]',
            f'|=[ i ]=[ {max(playerball.iframes, 0)} ]',
            f'|=[ E ]=[ {len(enemy_list)} ]',
            f'|=[ e ]=[ {round(enemy_timer, 2)} ]',
            f'|=[ M ]=[ {round(max_enemy_timer, 2)} ]',
            f'|=[ p ]=[ {len(particle_list)} ]',
             'J '
        ]
        for string in strings:
            text = default_font.render(string, False, (100, 100, 100))
            window.blit(text, (0, 20 * (strings.index(string) + 1) - 20))

        fuel_string = default_font.render(str(max(round(playerball.fuel, 1), 0.0)), False, (255, 255, 200) if playerball.fuel > 0 else (255, 0, 0))
        window.blit(fuel_string, (WIDTH/2 - fuel_string.get_width()/2, 50))

        combo_string = default_font.render(str(combo_multiplier), False, (140, 80, 140))
        window.blit(combo_string, (WIDTH/2 - combo_string.get_width()/2, 70))

        window.blit(destroyed_goal_sprite, (goal_destroyed["x"], goal_destroyed["y"]))
        window.blit(mine_sprite, (mine["x"]-5, mine["y"]-5))

    frame += 1
    pygame.display.flip()
    clock.tick(user_fps)

pygame.quit()

"""
TODO fix the fish boss because i absolutely fucking broke it 💀💀
TODO improve the visual effects
TODO add enemy variety
TODO add background stains (when enemies get killed, goals destroyed, dashes dashed etc.) # Crazy
TODO balance the grenades (or replace them with other projectiles)
TODO add more weaponry (perhaps lasers)
TODO fix floater texts destroying the fps
TODO make the fuel ball better somehow also bring back the old style thingities it had im not doing that today 💀
------------------------------------
DOING add a bossfight (fish boss real)
DOING add variety to gameplay (somehow idk) 
------------------------------------
DONE refactor the code to make it more readable
DONE fix the mine explosion behaving weirdly | it was literally a rounding error :wideskull:
DONE add kill combo bonuses
DONE fix game freezing shortly after dying (reason unknown)
DONE add a way to respawn LIKE WHY DIDN'T WE ADD THIS BEFORE
DONE add scoreboard
DONE fix occasional IndexError: pop from empty list on line 547 or 553 i forgor which one of them causes the error 
DONE improve ball handling
DONE add a simple background instead of the black void
DONE add sfx and bgm
DONE stylize the scoreboard
"""
# j <- literally the least used letter in the entire code :skull:
