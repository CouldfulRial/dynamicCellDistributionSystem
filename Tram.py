import pygame
import sys

# 初始化pygame
pygame.init()
# 设置参数
SCREEN_WIDTH = 1050
SCREEN_HEIGHT = 1015
BACKGROUND_COLOR = (255, 255, 255)
SWITCH_GREEN = (0, 255, 0)
SWITCH_RED = (255, 0, 0)
CIRCLE_COLOR = (173, 216, 230)  # Light blue color
LINE_COLOR = (0, 0, 0)
PROGRESSBAR_Y = SCREEN_HEIGHT - 100
PROGRESSBAR_WIDTH = 600
PROGRESSBAR_HEIGHT = 20
PROGRESS_COLOR = (0, 255, 0)
PROGRESSBAR_X = (SCREEN_WIDTH - PROGRESSBAR_WIDTH) // 2

dragging = False
coordinates = [(0, 1), (2, 5), (4, 4), (4, 6), (8, 8), (12, 9), (11, 15), (15, 20), (20, 16)]
times = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # An example timeline
max_time = times[-1]-1

# 开关设置
SWITCH_WIDTH = 30
SWITCH_HEIGHT = 30
SWITCH_X = (SCREEN_WIDTH - 860)
SWITCH_Y = (SCREEN_HEIGHT - 105)
switch_status = False  # 默认关闭

# Train data: starting_time, battery_count, current_percentage
trains = [
    {"start_time": 0, "battery_count": 50, "percentage": 0},
    {"start_time": 1, "battery_count": 20, "percentage": 0},
    {"start_time": 2, "battery_count": 500, "percentage": 0},
    {"start_time": 3, "battery_count": 250, "percentage": 0},
    {"start_time": 4, "battery_count": 350, "percentage": 0},
]
battery_warehouses = [
    {"position": coord, "battery_count": 20} for coord in coordinates[1:]
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def get_train_position(percentage):
    time = percentage * max_time
    for i in range(len(times) - 1):
        if times[i] <= time <= times[i + 1]:
            alpha = (time - times[i]) / (times[i + 1] - times[i])
            start_x, start_y = coordinates[i]
            end_x, end_y = coordinates[i + 1]
            x_position = (1 - alpha) * start_x + alpha * end_x
            y_position = (1 - alpha) * start_y + alpha * end_y
            return x_position * 50, y_position * 50  # We scale the coordinates for better visualization
    return -1, -1  # Outside of the defined time range


def draw_train(x, y, battery_count):
    pygame.draw.circle(screen, CIRCLE_COLOR, (int(x), int(y)), battery_count/20)

    # Add the battery count in the center of the circle
    font = pygame.font.SysFont(None, 25)
    text_surface = font.render("{:.2f}".format(battery_count), True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(int(x), int(y)))
    screen.blit(text_surface, text_rect)


def update_battery_warehouses(train_percentage, train):
    tolerance = 50
    for warehouse in battery_warehouses:
        x, y = warehouse["position"]
        train_x, train_y = get_train_position(train_percentage)

        distance = ((train_x - x*50) ** 2 + (train_y - y*50) ** 2) ** 0.5

        if distance < tolerance and warehouse["battery_count"] < 50:
            if train["battery_count"]>=70-warehouse["battery_count"]:
                train["battery_count"] =train["battery_count"]-(70-warehouse["battery_count"])
                warehouse["battery_count"] = 70
            else:
                warehouse["battery_count"]=warehouse["battery_count"]+train["battery_count"]
                train["battery_count"]=0

def lerp(a, b, t):
        """Linear interpolation between a and b."""
        return a + t * (b - a)
def get_color_for_battery(battery_count):
    if battery_count <= 0:
        t = -battery_count / 50.0  # Map the range [-50, 0] to [0, 1]
        r = int(lerp(255, 0, t))
        g = int(lerp(0, 255, t))
        b = 0
    elif battery_count <= 70:
        t = battery_count / 70.0  # Map the range [0, 70] to [0, 1]
        r = 0
        g = int(lerp(255, 0, t))
        b = int(lerp(0, 255, t))
    else:
        r, g, b = 0, 0, 255  # Just blue for counts above 70

    return (r, g, b)
def draw_battery_warehouses():
    for warehouse in battery_warehouses:
        x, y = warehouse["position"]
        x=50*x
        y=50*y
        color = get_color_for_battery(warehouse["battery_count"])
        pygame.draw.rect(screen, color, (x - 10, y + 10, 20, 20))  # Draw a yellow square below the coordinate point
        font = pygame.font.SysFont(None, 24)
        text = font.render("{:.2f}".format(warehouse["battery_count"]), True, (0, 0, 0))
        screen.blit(text, (x - 5, y + 35))
def draw_path():
    for i in range(1, len(coordinates)):
        start_x, start_y = coordinates[i - 1]
        end_x, end_y = coordinates[i]
        pygame.draw.line(screen, LINE_COLOR, (start_x * 50, start_y * 50), (end_x * 50, end_y * 50))


def draw_progress_bar(global_time):
    # Drawing the progress bar itself
    pygame.draw.rect(screen, (200, 200, 200), (PROGRESSBAR_X, PROGRESSBAR_Y, PROGRESSBAR_WIDTH, PROGRESSBAR_HEIGHT))
    pygame.draw.rect(screen, (0, 0, 0), (PROGRESSBAR_X + global_time * PROGRESSBAR_WIDTH - 2, PROGRESSBAR_Y, 4, PROGRESSBAR_HEIGHT))

    # Convert the global_time (range 0 to 1) to hours (range 0 to 24)
    total_hours = global_time * 24

    # Extract hours and minutes
    hours = int(total_hours)
    minutes = int((total_hours - hours) * 60)

    # Format time as HH:mm
    time_str = "{:02d}:{:02d}".format(hours, minutes)

    font = pygame.font.SysFont(None, 24)
    text = font.render(time_str, True, (0, 0, 0))
    text_width, text_height = font.size(time_str)

    # Calculate position for the text
    text_x = PROGRESSBAR_X + global_time * PROGRESSBAR_WIDTH - text_width / 2
    text_y = PROGRESSBAR_Y - text_height - 5  # 5 pixels gap

    # Ensure the text does not move out of screen
    text_x = min(max(text_x, PROGRESSBAR_X), PROGRESSBAR_X + PROGRESSBAR_WIDTH - text_width)
    screen.blit(text, (text_x, text_y))

def main():
    global dragging
    clock = pygame.time.Clock()
    auto_move = False
    global_time = 0  # This variable keeps track of the overall time progression
    BATTERY_DECREMENT = 0.1

    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_path()

        if auto_move:
            global_time += 0.001
            if global_time > 1:
                global_time=1
                BATTERY_DECREMENT=0
            for warehouse in battery_warehouses:
                warehouse["battery_count"] = max(-50, warehouse["battery_count"] - BATTERY_DECREMENT)

        for train in trains:
            train_elapsed_time = global_time * max_time - train["start_time"]
            if 0 <= train_elapsed_time <= 1:  # If the train is within its allowed time frame
                train["percentage"] = train_elapsed_time
                update_battery_warehouses(train["percentage"], train)  # Check and refill batteries
                x, y = get_train_position(train["percentage"])
                draw_train(x, y, train["battery_count"])
        draw_battery_warehouses()
        draw_progress_bar(global_time)
        switch_color = SWITCH_GREEN if auto_move else SWITCH_RED
        pygame.draw.rect(screen, switch_color, (SWITCH_X, SWITCH_Y, SWITCH_WIDTH, SWITCH_HEIGHT))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and PROGRESSBAR_X <= event.pos[
                0] <= PROGRESSBAR_X + PROGRESSBAR_WIDTH and PROGRESSBAR_Y <= event.pos[
                1] <= PROGRESSBAR_Y + PROGRESSBAR_HEIGHT:
                dragging = True
                auto_move = False

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False

            if event.type == pygame.MOUSEMOTION and dragging:
                mouse_x = event.pos[0]
                global_time = (mouse_x - PROGRESSBAR_X) / PROGRESSBAR_WIDTH
                global_time = max(0, min(1, global_time))
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 检查是否点击了开关
                if SWITCH_X <= event.pos[0] <= SWITCH_X + SWITCH_WIDTH and SWITCH_Y <= event.pos[
                    1] <= SWITCH_Y + SWITCH_HEIGHT:
                    auto_move = not auto_move  # 切换开关状态



        clock.tick(30)





if __name__ == "__main__":
    main()