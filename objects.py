import pygame, time, random

class StaticSprite:
    def __init__(self, sprite :pygame.surface.Surface, lifetime :float, location :tuple[int, int], window :pygame.surface.Surface, scale :float = 1.0, disintegration_speed :float = 3, random_rotation :bool= True) -> None:
        """sprite: surface object of the sprite
        lifetime: time the sprite is alive for
        location: location (x,y) where the sprite will spawn (the sprite is centred)
        window: the surface where the sprite will be rendered
        
        Optional arguments:
        scale: scale of the sprite
        disintegration_speed: how fast the sprite is faded out after its lifetime is completed
        random_rotation: give the sprite a random rotation when spawned?
        """

        self.lifetime = lifetime
        self.birth_time = time.time()
        self.opacity = 255
        self.window = window
        self.sprite = pygame.transform.rotate(sprite, random.random()*360) if random_rotation else sprite
        self.location = location
        self.active = True
        self.scale = scale
        self.disintegration = disintegration_speed

        self.spawn_location = (
            self.location[0] - self.sprite.get_width()/2,
            self.location[1] - self.sprite.get_height()/2,
        )

    def update(self):
        # check if life time has elapsed
        if time.time() - self.birth_time > self.lifetime:
            # If 5 seconds have elapsed, start fading the splat out
            self.opacity -= self.disintegration
            if self.opacity <= 0:
                self.active = False
        
        # Render the thingamajig
        self.sprite.set_alpha(self.opacity)
        self.window.blit(pygame.transform.scale_by(self.sprite, self.scale), self.spawn_location)