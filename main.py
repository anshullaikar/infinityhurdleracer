import pygame
import random
import logging

pygame.init()
screen_width = 800
screen_height = 600
game_display = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Hurdles")
clock = pygame.time.Clock()

# colors
black = (0, 0, 0)
white = (255, 255, 255)

# animation logic
walk_count = 0
left = False
right = False

walk_right_img = [pygame.image.load("files/R1.png"),
                  pygame.image.load("files/R2.png"),
                  pygame.image.load("files/R3.png"),
                  pygame.image.load("files/R4.png")]
walk_left_img = [pygame.image.load("files/L1.png"),
                 pygame.image.load("files/L2.png"),
                 pygame.image.load("files/L3.png"),
                 pygame.image.load("files/L4.png")]
hurdle_img = pygame.image.load("files/Hurdle.png")

runner_img = pygame.image.load('files/running_man.png')
bg_img = pygame.image.load('files/Background1.png')
standing_img = pygame.image.load("files/Standing.png")
runner_width = 50
runner_height = 50
c = 0
ground_height = 350
hurdle_height = 40
restart = True


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


BackGround = Background('files/Background1.png', [0, 0])

game_display.fill([255, 255, 255])
game_display.blit(BackGround.image, BackGround.rect)

hurdle_interval = random.randrange(3, 10)  # picks a random time to show next hurdle on screen


def hurdles(hurdle_x, hurdle_y):
    game_display.blit(hurdle_img, (hurdle_x, hurdle_y))


def score(count):
    font = pygame.font.SysFont(None, 25)
    text = font.render("Score: " + str(count), True, white)
    game_display.blit(text, (0, 0))


def runner(x, y):
    global walk_count
    global left
    global right
    if (walk_count + 1) > 20:
        walk_count = 0

    if left:
        game_display.blit(walk_left_img[walk_count // 5], (x, y))
        walk_count += 1
    elif right:
        game_display.blit(walk_right_img[walk_count // 5], (x, y))
        walk_count += 1
    else:
        game_display.blit(standing_img, (x, y))


def text_objects(text, font):
    text_surf = font.render(text, True, white)
    return text_surf, text_surf.get_rect()


def message_display(text):
    large_text = pygame.font.Font('freesansbold.ttf', 30)
    text_surf, text_rect = text_objects(text, large_text)
    text_rect.center = (screen_width / 2, screen_height / 4)
    pygame.draw.rect(game_display, black, text_rect)
    game_display.blit(text_surf, text_rect)
    pygame.display.update()


desired_fps = 45


def oof():
    message_display("you lose! Press r to restart or q to quit")


def jumping(time1, jump_speedy, is_jumping, y_pos):
    vel_y = 0
    if is_jumping:
        t2: float = pygame.time.get_ticks()
        dt: float = (t2 - time1) / 1000  # calculating time passed from beginning of jump for v = u + at
        vel_y = jump_speedy - dt * 30
        if y_pos > (ground_height - runner_height):
            y_pos = ground_height - runner_height
            vel_y = 0
            is_jumping = False
    return vel_y, is_jumping, y_pos


def game_loop(continue_game=True, game_speed=0):
    global hurdle_height
    global restart
    global walk_count
    global left
    global right
    restart = False
    x = screen_width * 0.5
    y = ground_height - runner_height
    change_x = 7
    change_y = 0
    hurdle_speed = 6
    hurdle_start_x = screen_width
    hurdle_start_y = ground_height - hurdle_height
    hurdle_width = 20
    can_move = True
    is_jump = False
    crashed = False
    jump_speed = 9.5
    dodged = 0
    game_speed_multiplier = 1

    while continue_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continue_game = False

        keys = pygame.key.get_pressed()
        left_boolean = (keys[pygame.K_LEFT] or keys[pygame.K_a]) and x > -runner_width  # check whether left key is
        # being pressed
        right_boolean = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and x < (screen_width - runner_width)  # check
        # whether right key is being pressed
        if can_move:
            if left_boolean:
                x -= change_x
                left = True
                right = False
                game_speed = 1 * game_speed_multiplier
            elif right_boolean:
                x += change_x
                right = True
                left = False
                game_speed = 2 * game_speed_multiplier
            else:
                right = True
                left = left
                game_speed = 2 * game_speed_multiplier
            if not is_jump:
                if (keys[pygame.K_UP] or keys[pygame.K_w]) and y > change_y:
                    is_jump = True
                    t1 = pygame.time.get_ticks()
                if keys[pygame.K_SPACE]:
                    is_jump = True
                    t1 = pygame.time.get_ticks()  # getting time when space is pressed to calculate total time during
                    # jump
        if keys[pygame.K_q]:
            continue_game = False
            restart = False
        if keys[pygame.K_r]:
            restart = True
            continue_game = False

        game_display.fill(white)
        game_display.blit(BackGround.image, BackGround.rect)
        score(dodged)
        hurdles(hurdle_start_x, hurdle_start_y)
        if not crashed:
            hurdle_start_x -= hurdle_speed
        runner(x, y)
        pygame.display.update()
        if hurdle_start_x < -hurdle_width and not crashed:
            hurdle_start_x = screen_width
            dodged += 1
            if dodged < 9:  # reaching a max speed in the game
                hurdle_speed *= 1.15
        if (hurdle_start_x < x + runner_width/2 < hurdle_start_x + hurdle_width) and (
                y + runner_height/1.2 >= ground_height - hurdle_height):
            crashed = True
            y_crash = y
        if x <= -runner_width:
            crashed = True
        if crashed:
            can_move = False
            try:
                y = y_crash
            except UnboundLocalError:
                pass
            oof()
        if is_jump:
            change_y, is_jump, y = jumping(t1, jump_speed, is_jump, y)
        if not crashed:  # pause movement when game crashed
            x -= game_speed
            y -= change_y
        clock.tick(desired_fps)
        if game_speed_multiplier < 3.3:
            game_speed_multiplier *= 1.0005
        elif game_speed_multiplier > 3.3 and change_x < 12:
            change_x *= 1.002
            game_speed_multiplier *= 1.0008
        logging.info(game_speed_multiplier)
        game_display.blit(runner_img, (runner_width, runner_height))


while restart:
    game_loop()
    walk_count = 0
    c += 1
    print(c)
pygame.quit()
