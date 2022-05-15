import logging

c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_handler.setFormatter(c_format)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(c_handler)


import pygame
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from my_sprites import Line, Player


def check_collision(player, all_lines):
    collision = False
    # logger.debug(player.edge_rect.x)

    for l in all_lines:
        if player.edge_rect.clipline(l.start_position, l.end_position):
            logger.debug("BOOOM")
            collision = True
    return collision

if __name__ == "__main__":
    pygame.init()

    # Set up the drawing window
    screen = pygame.display.set_mode([800, 400])
    clock = pygame.time.Clock()

    # Runs until the user quits
    running = True
    line = Line(screen, [700, 150], [700, 350], 5)
    line2 = Line(screen, [250, 300], [100, 100], 5, clockwise=False)
    all_lines = [line, line2]

    player = Player(screen, (300, 300))

    while running:
        
        # checks if the user closed the window
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    running = False
            
            elif event.type == pygame.QUIT:
                running = False

        # Fill the background with white
        screen.fill((0, 0, 0))
        pressed_keys = pygame.key.get_pressed()
        player.draw(pressed_keys)
        player.move()
        for l in all_lines:
            l.update()
        
        is_collision = check_collision(player, all_lines)

        if is_collision:
            running = False

        # Flip the display (update frame)
        pygame.display.flip()
        clock.tick(20)

    # Ends the program
    pygame.quit()