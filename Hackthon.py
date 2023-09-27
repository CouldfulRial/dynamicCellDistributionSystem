import sys
import pygame
from pygame.locals import *
import math

# 初始化Pygame
pygame.init()

# 设置窗口的大小
WIDTH, HEIGHT = 1050, 1015
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Renewable Energy Supply")

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GREY = (200, 200, 200)

# 定义能源类型
SOLAR = "solar"
WIND = "wind"
HYDRO = "hydro"

# 定义初始天气
weather = "sunny"

# 定义初始时间
time = 48  # 12:00

# 定义字体
font = pygame.font.Font(None, 36)

#计算supply的大小
def calculate_supply(energy_type, time, weather):
    hour = time // 4
    if energy_type == SOLAR:
        # 太阳能在白天达到最大，在夜间为0
        supply = max(0, 100 - abs(hour - 12) * 100 / 6)
        if weather == "rainy" or weather == "cloudy":
            supply *= 0.5  # 雨天或阴天时太阳能输出减半
    elif energy_type == WIND:
        # 风电根据正弦波变化
        supply = 50 + 50 * math.sin(math.radians(hour * 15))
        if weather == "rainy":
            supply *= 1.2  # 风电在雨天时增加
    elif energy_type == HYDRO:
        # 水电保持稳定输出
        supply = 90 if weather == "rainy" else 80  # 雨天时水电输出提高到90
    return supply

#传统能源互补
def draw_gray_circle(solar_supply, wind_supply, hydro_supply):
    total_supply = solar_supply + wind_supply + hydro_supply
    remaining = int(400 - total_supply)
    pos = (WIDTH - 100, HEIGHT // 2)  # 您可以根据需要更改这个位置
    pygame.draw.circle(screen, GREY, pos, 50)  # 您可以根据需要更改半径大小
    text = font.render(str(remaining), True, WHITE)
    screen.blit(text, (pos[0] - text.get_width() // 2, pos[1] - text.get_height() // 2))

#变色逻辑
def draw_circle(energy_type, pos, time, weather):
    supply = calculate_supply(energy_type, time, weather)
    r = min(255, max(0, (100 - supply) * 2.55))
    g = min(255, max(0, supply * 2.55))
    color = (r, g, 0)  # 绿到红

    pygame.draw.circle(screen, color, pos, 50)
    text = font.render(str(int(supply)), True, WHITE)
    screen.blit(text, (pos[0] - text.get_width() // 2, pos[1] - text.get_height() // 2))

#时间轴
def draw_time_slider(time):
    pygame.draw.rect(screen, GREY, (50, HEIGHT - 150, WIDTH - 100, 10))
    pygame.draw.circle(screen, WHITE, (50 + int(time * (WIDTH - 100) / 96), HEIGHT - 145), 15)
    hour = int(time // 4)
    minute = int((time % 4) * 15)
    time_text = font.render(f"{hour:02d}:{minute:02d}", True, WHITE)
    screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT - 175))

auto_mode = False

#
def draw_auto_button():
    color = GREEN if auto_mode else GREY
    pygame.draw.polygon(screen, color, [(10, HEIGHT - 195), (30, HEIGHT - 185), (10, HEIGHT - 175)])


def draw_buttons(weather):
    buttons = ["sunny", "cloudy", "rainy"]
    x = WIDTH // 2 - 120
    for button in buttons:
        color = GREEN if button == weather else GREY
        pygame.draw.rect(screen, color, (x, HEIGHT - 100, 100, 50))  # 修改按钮大小
        button_text = font.render(button, True, WHITE)
        screen.blit(button_text, (x + 10, HEIGHT - 90))
        x += 120

icon_size = (50, 50)  # 用您希望的宽度和高度替换这个值

wind_icon = pygame.image.load('wind_icon.png').convert_alpha()
wind_icon = pygame.transform.scale(wind_icon, icon_size)

solar_icon = pygame.image.load('solar_icon.png').convert_alpha()
solar_icon = pygame.transform.scale(solar_icon, icon_size)

hydro_icon = pygame.image.load('hydro_icon.png').convert_alpha()
hydro_icon = pygame.transform.scale(hydro_icon, icon_size)


def draw_icon_and_value(icon, pos, supply):
    screen.blit(icon, (pos[0] - icon.get_width() // 2, pos[1] - icon.get_height() // 2))
    value_text = font.render(str(int(supply)), True, WHITE)
    screen.blit(value_text, (pos[0] - value_text.get_width() // 2, pos[1] + icon.get_height() // 2 + 10))

def main():
    global time, weather, auto_mode
    clock = pygame.time.Clock()
    running = True
    dragging = False
    while running:
        screen.fill(BLACK)
        solar_supply = int(calculate_supply(SOLAR, time, weather))
        wind_supply = int(calculate_supply(WIND, time, weather))
        hydro_supply = int(calculate_supply(HYDRO, time, weather))
#外面的大圆
        draw_circle(SOLAR, (200, 200), time, weather)
        draw_circle(WIND, (400, 200), time, weather)
        draw_circle(HYDRO, (600, 200), time, weather)
        draw_time_slider(time)
        draw_buttons(weather)
        draw_auto_button()
#传统能源需求
        draw_gray_circle(solar_supply, wind_supply, hydro_supply)
#图标和数字

        draw_icon_and_value(solar_icon, (200, 200), calculate_supply(SOLAR, time, weather))
        draw_icon_and_value(wind_icon, (400, 200), calculate_supply(WIND, time, weather))
        draw_icon_and_value(hydro_icon, (600, 200), calculate_supply(HYDRO, time, weather))


        if auto_mode:
            time = (time + 1) % 97  # 自动增加时间

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                # 检查时间滑块
                if HEIGHT - 155 < y < HEIGHT - 135 and 50 < x < WIDTH - 50:
                    dragging = True
                    time = max(0, min(96, (x - 50) * 96 / (WIDTH - 100)))
                # 检查天气按钮
                elif HEIGHT - 100 < y < HEIGHT - 60:
                    if WIDTH // 2 - 120 < x < WIDTH // 2 - 30:
                        weather = "sunny"
                    elif WIDTH // 2 < x < WIDTH // 2 + 90:
                        weather = "cloudy"
                    elif WIDTH // 2 + 120 < x < WIDTH // 2 + 210:
                        weather = "rainy"
                # 检查自动按钮
                elif HEIGHT - 200 < y < HEIGHT - 170 and 0 < x < 30:
                    auto_mode = not auto_mode  # 改变自动模式状态

            elif event.type == MOUSEBUTTONUP:
                dragging = False
            elif event.type == MOUSEMOTION and dragging:
                x, y = event.pos
                time = max(0, min(96, (x - 50) * 96 / (WIDTH - 100)))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
