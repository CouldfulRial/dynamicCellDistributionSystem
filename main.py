import pygame
from pygame.locals import QUIT

# Initialize pygame
pygame.init()

# Load image
image_path = "../../pythonProject1/dynamicCellDistributionSystem/src/mapOnlyRoadBlackTracex0.5.png"
background_image = pygame.image.load(image_path)

# Set the window size to the image size
screen_width, screen_height = background_image.get_size()
screen = pygame.display.set_mode((screen_width, screen_height))

# Define lists of polygons
polygons = [
    [(50, 50), (150, 50), (200, 100), (150, 150), (50, 150)],
    [(250, 50), (300, 50), (350, 100), (300, 150), (250, 150)],
    [(100, 200), (200, 250), (150, 300)]
]

# Define the color for your polygon (e.g., red)
R = 255
G = 0
B = 0
increment = 1

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    # Clear the screen with a color (optional, but can help with visual artifacts)
    screen.fill((255, 255, 255))

    # Draw the polygons
    for polygon_points in polygons:
        pygame.draw.polygon(screen, (R, G, B), polygon_points)

    # Update the colour
    R = R - increment
    G = G + increment
    if R >= 255 or G >= 255:
        increment = -increment

    # Blit the image onto the screen
    screen.blit(background_image, (0, 0))

    # Update display
    pygame.display.flip()

pygame.quit()
