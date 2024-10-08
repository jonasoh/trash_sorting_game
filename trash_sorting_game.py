import pygame
import random
import time
import os

screen_width, screen_height = 1280, 720
lane_y_positions = [50, 150, 250, 350]
flower_x_positions = [256, 512, 768, 1024]
lane_height = 50
green = (34, 109, 14)
grey = (169, 169, 169)
white = (255, 255, 255)
bus_speed_per_frame = 5


def ls(x):
    return pygame.image.load('substrates/' + x)


substrates = {
    # substrates are classified by the amount of biogas they generate (measured as the
    # number of meters a bus will travel on one kg of substrate), and how good digestate they generate
    # (how much nitrogen is in one kg of the substrate)
    pygame.K_a: {
        'image': [
            ls('banana1.png'),
            ls('banana2.png'),
            ls('banana3.png'),
            ls('banana4.png'),
        ],
        'biogas': 1810,
        'digestate': 20,
    },
    pygame.K_b: {
        'image': [
            ls('fish1.png'),
            ls('fish2.png'),
            ls('fish3.png'),
            ls('fish4.png'),
        ],
        'biogas': 18900,
        'digestate': 220,
    },
    pygame.K_c: {
        'image': [
            ls('eggshells1.png'),
            ls('eggshells2.png'),
        ],
        'biogas': 0,
        'digestate': 0,
    },
    pygame.K_d: {
        'image': [
            ls('candy1.png'),
            ls('candy2.png'),
        ],
        'biogas': 7250,
        'digestate': 0,
    },
    pygame.K_e: {
        'image': [
            ls('bread1.png'),
            ls('bread2.png'),
            ls('bread3.png'),
            ls('bread4.png'),
        ],
        'biogas': 8700,
        'digestate': 100,
    },
    pygame.K_f: {
        'image': [ls('applecore1.png'), ls('applecore2.png')],
        'biogas': 1800,
        'digestate': 20,
    },
    pygame.K_g: {
        'image': [ls('peels1.png'), ls('peels2.png')],
        'biogas': 2180,
        'digestate': 20,
    },
    pygame.K_h: {
        'image': [ls('bones1.png')],
        'biogas': 0,
        'digestate': 0,
    },
    pygame.K_i: {
        'image': [ls('coffeegrounds1.png')],
        'biogas': 4060,
        'digestate': 10,
    },
    pygame.K_j: {
        'image': [ls('yogurt1.png')],
        'biogas': 1930,
        'digestate': 40,
    },
    pygame.K_k: {
        'image': [ls('dirt1.png')],
        'biogas': 0,
        'digestate': 0,
    },
    pygame.K_l: {'image': [ls('flowers1.png')], 'biogas': 6040, 'digestate': 70},
    pygame.K_m: {'image': [ls('plastic1.png')], 'biogas': 0, 'digestate': 0},
    pygame.K_n: {'image': [ls('oil1.png')], 'biogas': 32940, 'digestate': 0},
    pygame.K_o: {'image': [ls('shrimp1.png')], 'biogas': 11340, 'digestate': 130},
    pygame.K_p: {
        'image': [ls('paper1.png'), ls('paper2.png')],
        'biogas': 7400,
        'digestate': 0,
    },
    pygame.K_q: {'image': [ls('cutlery1.png')], 'biogas': 0, 'digestate': 0},
    pygame.K_r: {'image': [ls('pasta1.png')], 'biogas': 5080, 'digestate': 70},
    pygame.K_s: {
        'image': [ls('cheese1.png'), ls('cheese2.png')],
        'biogas': 9670,
        'digestate': 250,
    },
    pygame.K_t: {
        'image': [
            ls('meatballs1.png'),
            ls('meatballs2.png'),
            ls('meatballs3.png'),
            ls('meatballs4.png'),
        ],
        'biogas': 12090,
        'digestate': 210,
    },
}

km_per_pixel = sum(x['biogas'] for x in substrates.values()) / 1100
km_per_pixel /= 1.4
bus_keys = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}
scores = {x: {'biogas': 0, 'digestate': 0} for x in range(4)}


class Bus(pygame.sprite.Sprite):
    def __init__(self, image, x, y, sel_image):
        super().__init__()
        self.orig_image = image
        self.selected_image = sel_image
        self.image = self.orig_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.target_x = x
        self.movement_per_frame = 0
        self.selected = False

    def move(self, distance):
        self.target_x += distance
        # Calculate the movement per frame based on a fixed speed, considering the direction
        self.movement_per_frame = (
            bus_speed_per_frame if distance >= 0 else -bus_speed_per_frame
        )

    def reset(self):
        self.rect.x = 30
        self.target_x = 30

    def update(self):
        if self.selected:
            self.image = self.selected_image
        else:
            self.image = self.orig_image

        if self.rect.x != self.target_x:  # move the bus smoothly
            self.rect.x += self.movement_per_frame
            if abs(self.rect.x - self.target_x) < abs(self.movement_per_frame):
                self.rect.x = self.target_x  # snap to final position if close enough


class Flower(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.midbottom = (x, y)
        self.scale = 1

    def grow(self, delta):
        self.scale += delta * 1.2

    def reset(self):
        self.scale = 1

    def update(self):
        self.scale_factor = min(self.scale, 3)

        new_width = int(self.original_image.get_width() * self.scale_factor)
        new_height = int(self.original_image.get_height() * self.scale_factor)
        if new_width > 0 and new_height > 0:  # Ensure valid dimensions
            scaled_image = pygame.transform.scale(
                self.original_image, (new_width, new_height)
            )
            self.image = scaled_image
            self.rect = self.image.get_rect()
            self.rect.midbottom = (self.x, self.y)


class RotatingScalingSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y, duration):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.original_image.get_rect(center=(x, y))
        self.x = x
        self.y = y
        self.angle = 0
        self.scale_factor = 0.0  # starting scale factor (0%)
        self.duration = duration  # duration for full cycle (scale-up and scale-down)
        self.start_time = pygame.time.get_ticks()  # record when the effect started

    def update(self):
        # Calculate elapsed time since the effect started
        elapsed_time = (
            pygame.time.get_ticks() - self.start_time
        ) / 1000.0  # in seconds

        progress = elapsed_time / self.duration

        if progress >= 1.0:
            self.kill()
            return

        # Scale factor changes based on progress (from 0.0 to 5.0 and back to 0.0)
        if progress < 0.5:
            # scale from 0% (0.0) to 200% (2.0) during the first half of the duration
            self.scale_factor = 2.0 * (progress * 2)
        else:
            # scale from 200% (2.0) back down to 0% (0.0) during the second half
            self.scale_factor = 2.0 - 2.0 * ((progress - 0.5) * 2)

        self.angle += 15 + progress * 30

        # Scale the image relative to the original size
        new_width = int(self.original_image.get_width() * self.scale_factor)
        new_height = int(self.original_image.get_height() * self.scale_factor)
        if new_width > 0 and new_height > 0:  # Ensure valid dimensions
            scaled_image = pygame.transform.scale(
                self.original_image, (new_width, new_height)
            )
            rotated_image = pygame.transform.rotate(scaled_image, self.angle)

            # Update the image and the rect
            self.image = rotated_image
            self.rect = self.image.get_rect(center=(self.x, self.y))


def splat():
    random.choice(sounds).play()


def draw_scores():
    for i in range(4):
        d_score_surface = font_scores.render(str(scores[i]['digestate']), True, white)
        d_score_rect = d_score_surface.get_rect(center=(flower_x_positions[i], 700))

        b_score_surface = font_scores.render(str(scores[i]['biogas']), True, white)

        screen.blit(d_score_surface, d_score_rect)
        screen.blit(b_score_surface, (1100, lane_y_positions[i] - 55))


def reset():
    global scores
    for bus in buses:
        bus.reset()
    for flower in flowers:
        flower.reset()
    scores = {x: {'biogas': 0, 'digestate': 0} for x in range(4)}


# initialize pygame
pygame.init()
random.seed()

# create screen
screen = pygame.display.set_mode(
    (screen_width, screen_height), pygame.FULLSCREEN | pygame.SCALED
)
pygame.display.set_caption('Biogasspelet')
pygame.mixer.init()

# bus sprites
bus_image = pygame.image.load('sprites/bus.png')
sel_image = pygame.image.load('sprites/bus_sel.png')

buses = [Bus(bus_image, 30, lane_y_positions[i], sel_image) for i in range(4)]
current_bus = -1  # initially, no bus is selected
all_buses = pygame.sprite.Group(buses)

# flower sprites
flower_images = [
    pygame.image.load('sprites/flower1.png'),
    pygame.image.load('sprites/flower1.png'),
    pygame.image.load('sprites/flower1.png'),
    pygame.image.load('sprites/flower1.png'),
]

flowers = [Flower(flower_images[i], flower_x_positions[i], 700) for i in range(4)]
all_flowers = pygame.sprite.Group(flowers)

# flying trash
trash_group = pygame.sprite.Group()

# sound files
sounds = [
    pygame.mixer.Sound(os.path.join('sounds', file))
    for file in os.listdir('sounds')
    if file.endswith('.wav')
    and not os.path.basename(file).startswith('._')  # macos idiot files
]

font_large = pygame.font.SysFont('Arial', 180)  # large font for display
font_scores = pygame.font.SysFont('Arial', 48)

# selected bus display timer
selected_display_time = 2  # display time in seconds
selection_start_time = None
selection_displaying = False

# game loop
running = True
clock = pygame.time.Clock()
while running:
    screen.fill(green)

    # draw lanes
    for y in lane_y_positions:
        pygame.draw.rect(
            screen, grey, (0, y - 5, screen_width, lane_height)
        )  # grey lanes
        for x in range(10, screen_width, 30):
            pygame.draw.rect(screen, white, (x, y, 10, 4))
            pygame.draw.rect(screen, white, (x, y + lane_height - 15, 10, 4))

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL:
                pygame.display.toggle_fullscreen()
            elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                reset()
            elif event.key in bus_keys:
                current_bus = bus_keys[event.key]
                selection_start_time = time.time()
                selection_displaying = True
            elif event.key in substrates and current_bus >= 0:
                d = substrates[event.key]
                trash = RotatingScalingSprite(
                    random.choice(d['image']),
                    x=random.randint(
                        int(0.15 * screen_width), int(0.85 * screen_width)
                    ),
                    y=random.randint(
                        int(0.15 * screen_height), int(0.85 * screen_height)
                    ),
                    duration=2.0,
                )
                trash_group.add(trash)
                splat()
                buses[current_bus].move(int(d['biogas'] / km_per_pixel))
                scores[current_bus]['biogas'] += d['biogas']
                scores[current_bus]['digestate'] += d['digestate']
                flowers[current_bus].grow(d['digestate'] / 1000)
                current_bus = -1
            elif event.key == pygame.K_ESCAPE:
                running = False

    for bus in all_buses.sprites():
        bus.selected = False
    if current_bus >= 0:
        buses[current_bus].selected = True

    # show large number for selected bus with fade-out effect
    if selection_displaying and current_bus >= 0:
        elapsed_time = time.time() - selection_start_time
        if elapsed_time < selected_display_time:
            selected_text = font_large.render(str(current_bus + 1), True, white)

            # create a surface with alpha for the fade-out effect
            selected_text_surface = pygame.Surface(
                (selected_text.get_width(), selected_text.get_height()), pygame.SRCALPHA
            )

            # calculate alpha for the fade effect
            fade_alpha = max(0, 255 - int((elapsed_time / selected_display_time) * 255))

            # render the text on the transparent surface
            selected_text_surface.fill((0, 0, 0, 0))
            selected_text_surface.blit(selected_text, (0, 0))  # blit the rendered text
            selected_text_surface.set_alpha(fade_alpha)

            screen.blit(
                selected_text_surface,
                (
                    screen_width // 2 - selected_text.get_width() // 2,
                    screen_height // 2 - selected_text.get_height() // 2,
                ),
            )
        else:
            selection_displaying = False

    for sg in [all_buses, all_flowers, trash_group]:
        sg.update()
        sg.draw(screen)

    draw_scores()

    pygame.display.flip()
    clock.tick(30)  # control frame rate

pygame.quit()
