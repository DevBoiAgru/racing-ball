import random, math, time, pygame
pygame.init()


class Ball:
    def __init__(self, x, y, x_vel, y_vel, x_acc, y_acc, radius, sprite):
        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.x_acc = x_acc
        self.y_acc = y_acc
        self.radius = radius
        self.sprite = sprite

    def draw(self):
        window.blit(self.sprite, (self.x - self.radius + shake_offsets["x"], self.y - self.radius + shake_offsets["y"]))

    def handle_movement(self, time_delta):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]: 
            self.y_vel -= self.y_acc * time_delta

        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]: 
            self.y_vel += self.y_acc * time_delta

        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]: 
            self.x_vel += self.x_acc * time_delta

        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]: 
            self.x_vel -= self.x_acc * time_delta

        if keys_pressed[pygame.K_LCTRL]:
            self.x_vel = 0
            self.y_vel = -0.2 * time_delta

        # TODO add time_delta to it without causing a ZeroDivisionError
        self.x_vel /= 1.013
        self.y_vel /= 1.013

    def update_pos(self):
        self.y += self.y_vel
        self.x += self.x_vel

    def shift_pressed(self):
        global mouse_pos, last_shift_press_time
        dist_x = self.x - mouse_pos[0]
        dist_y = self.y - mouse_pos[1]
        total_dist = math.sqrt(dist_x**2 + dist_y**2)
        x_factor = dist_x / total_dist
        y_factor = dist_y / total_dist

        # set player speed to a value, add extra depending on how much velocity direction and player-cursor direction match 
        angle = dot_product([self.x_vel, self.y_vel], [-x_factor, -y_factor])

        alignment_multiplier = (1 - angle / 180) ** 0.8

        self.x_vel = 8 * -x_factor + self.x_vel * alignment_multiplier
        self.y_vel = 8 * -y_factor + self.y_vel * alignment_multiplier

        shake_offsets["max"] += 8

        last_shift_press_time = time.time()

    def window_collision(self):
        global bounce_factor
        # right border
        if self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.x_vel *= -bounce_factor

        # left border
        if self.x < self.radius:
            self.x = self.radius
            self.x_vel *= -bounce_factor

        # top border
        if self.y < self.radius:
            self.y = self.radius
            self.y_vel *= -bounce_factor

        # bottom borders
        if self.y > HEIGHT - self.radius:
            self.y = HEIGHT - self.radius
            self.y_vel *= -bounce_factor

    def do_the_things(self):
        global time_delta
        self.handle_movement(time_delta)
        self.update_pos()
        self.window_collision()


class Spritesheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename)

    # image at (x, y, x sprite size, y sprite size)
    def image_at(self, rectangle):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size)
        image.blit(self.sheet, (0, 0), rect)
        image.set_colorkey((0, 0, 0))
        image.convert_alpha()
        return image


def do_shake_offsets():
    shake_offsets["x"] = random.randint(int(-shake_offsets["max"]), int(shake_offsets["max"])) if shake_offsets["max"] >= 1 else 0
    shake_offsets["y"] = random.randint(int(-shake_offsets["max"]), int(shake_offsets["max"])) if shake_offsets["max"] >= 1 else 0

    shake_offsets["max"] /= 1.05

def do_the_text():
    x_pos_text = font_default.render(str(round(player.x)), False, (100, 100, 100))
    window.blit(x_pos_text, (player.x + 20, player.y - 20))

    y_pos_text = font_default.render(str(round(player.y)), False, (100, 100, 100))
    window.blit(y_pos_text, (player.x + 20, player.y))

def dot_product(vec_1: list, vec_2: list) -> float:
    return vec_1[0] * vec_2[0] + vec_1[1] * vec_2[1]

def draw_cool_lines():
    pygame.draw.line(window, RED, (player.x, player.y), (mouse_pos[0], player.y)) # x distance
    pygame.draw.line(window, BLUE, (mouse_pos[0], mouse_pos[1]), (mouse_pos[0], player.y)) # y distance
    pygame.draw.line(window, (100, 100, 100), (0, 0), (player.x, player.y))
    pygame.draw.line(window, (160, 160, 160), (0, 0), (mouse_pos[0], mouse_pos[1]))

    dist_x = player.x - mouse_pos[0]
    dist_y = player.y - mouse_pos[1]
    total_dist = math.sqrt(dist_x**2 + dist_y**2)
    x_factor = dist_x / total_dist
    y_factor = dist_y / total_dist

    pygame.draw.line(window, YELLOW, (player.x, player.y), (player.x + x_factor * 30, player.y + y_factor * 30)) # away from cursor
    pygame.draw.line(window, MAGENTA, (player.x, player.y), (player.x + x_factor * -30, player.y + y_factor * -30)) # to cursor
    pygame.draw.line(window, GREEN, (player.x, player.y), (player.x + player.x_vel * 4, player.y + player.y_vel * 16)) # velocity (exagerated)

# to make it resizable
def draw_fg():
    window.blit(corner_tl, (0, 0))
    window.blit(corner_bl, (0, HEIGHT - 18))
    window.blit(corner_br, (WIDTH - 18, HEIGHT - 18))
    window.blit(corner_tr, (WIDTH - 18, 0))
    pygame.draw.rect(window, (255, 255, 255), (0, 0, WIDTH, 11)) # top
    pygame.draw.rect(window, (255, 255, 255), (0, 0, 11, HEIGHT)) # left
    pygame.draw.rect(window, (255, 255, 255), (0, HEIGHT - 11, WIDTH, HEIGHT)) # bottom
    pygame.draw.rect(window, (255, 255, 255), (WIDTH - 11, 0, WIDTH, HEIGHT)) # right

def draw_bg():
    x_size = drawn_bg.get_width()
    y_size = drawn_bg.get_height()

    rows = math.ceil(HEIGHT / y_size)
    cols = math.ceil(WIDTH / x_size)

    for row in range(rows):
        for col in range(cols):
            x = col * x_size
            y = row * y_size
            window.blit(drawn_bg, (x, y))

def tick():
    global draw_crosshair_at, mouse_pos, running, events, ticks_done, HEIGHT, WIDTH, ticks_done_in_last_second, tps_timer, tps, drawn_bg
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            break

        if event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            WIDTH = window.get_width()
            HEIGHT = window.get_height()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            shake_offsets["max"] += 10

        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            print("> ", end="")
            exec(input())

        if event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT:
            player.shift_pressed()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            if drawn_bg == bg_0:
                drawn_bg = bg_1
            else:
                drawn_bg = bg_0

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
            break

            
    mouse_pos = pygame.mouse.get_pos()
    draw_crosshair_at = [coordinate - 11.5 for coordinate in list(mouse_pos)]

    player.do_the_things()
    do_shake_offsets()
    ticks_done += 1
    ticks_done_in_last_second += 1
    if current_time - tps_timer > 1:
        tps = f"{ticks_done_in_last_second} tps"
        ticks_done_in_last_second = 0
        tps_timer = current_time

def frame():
    global WIDTH, tps, fps, frames_done_in_last_second, fps, fps_timer
    draw_bg()
    do_the_text()
    draw_cool_lines()
    player.draw()
    draw_fg()
    window.blit(spr_crosshair, draw_crosshair_at)

    frames_done_in_last_second += 1
    if current_time - fps_timer > 1:
        fps = f"{frames_done_in_last_second} fps"
        frames_done_in_last_second = 0
        fps_timer = current_time

    fps_text = font_default.render(fps, False, GREEN)
    tps_text = font_default.render(tps, False, YELLOW)
    window.blit(fps_text, (WIDTH/2 - fps_text.get_width()/2, 20))
    window.blit(tps_text, (WIDTH/2 - tps_text.get_width()/2, 40))
    pygame.display.flip()


WIDTH, HEIGHT = 1040, 720

window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Racing ball b1")
pygame.mouse.set_visible(0)

spr_a = pygame.image.load("assets/spr/a.png")
pygame.display.set_icon(spr_a)
bg_0 = pygame.image.load("assets/spr/bg_0.png")
bg_1 = pygame.image.load("assets/spr/bg_1.png")
drawn_bg = bg_0
spr_crosshair = pygame.image.load("assets/spr/crosshair.png")
fg_corners = Spritesheet("assets/spr/fg_corners.png")
corner_tl = fg_corners.image_at((0, 0, 18, 18))
corner_bl = fg_corners.image_at((19, 0, 18, 18))
corner_br = fg_corners.image_at((38, 0, 18, 18))
corner_tr = fg_corners.image_at((57, 0, 18, 18))

# too lazy to write these out every time lmao
BLACK   = (0,   0,   0)
RED     = (255, 0,   0)
GREEN   = (0,   255, 0)
BLUE    = (0,   0,   255)
YELLOW  = (255, 255, 0)
MAGENTA = (255, 0,   255)
CYAN    = (0,   255, 255)
WHITE   = (255, 255, 255)

fps = 60
font_default = pygame.font.Font("assets/VCR_OSD_MONO_1.001.ttf", 20)
shake_offsets = {"x": 0, "y": 0, "max": 0}
bounce_factor = 0.9
last_shift_press_time = 0
last_frame_time = 0
last_tick_time = 0

tickrate = 300
framerate = 60

ticks_done = 0
frames_done = 0

ticks_done_in_last_second = 0
tps_timer = 0
tps = ""

frames_done_in_last_second = 0
fps_timer = 0
fps = ""

player = Ball(600, 300, 0, 0, 10, 10, 6, spr_a)

clock = pygame.time.Clock()
running = True

while running:
    draw_frame_every_n_ticks = round(tickrate / framerate) # a very
    events = pygame.event.get()

    current_time = time.time()
    time_delta = current_time - last_tick_time

    tick()
    last_tick_time = current_time

    if ticks_done % draw_frame_every_n_ticks == 0:
        frame()
        last_frame_time = current_time

    clock.tick(tickrate)

pygame.quit()