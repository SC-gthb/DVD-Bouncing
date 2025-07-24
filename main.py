import pygame
import asyncio
import random
from os.path import join, exists
from os import makedirs
import json

pygame.init()
S_W, S_H = 1280, 720
screen = pygame.display.set_mode((S_W, S_H))
pygame.display.set_caption("DVD Bouncing")
pygame.display.set_icon(pygame.image.load(join("assets","dvd-icon.png")).convert_alpha())
font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 36)
button_font = pygame.font.Font(None, 26)

paused = False
direction = pygame.Vector2(1, 1)
clock = pygame.Clock()

dvd_img = pygame.image.load(join("assets","dvd.png")).convert_alpha()
dvd_dir = pygame.Vector2(1, 1)
dvd_vel = 100
dvd_rect = dvd_img.get_frect(center=(S_W/2, S_H/2))

DATA_DIR = "data"
COLORS_FILE = join(DATA_DIR, "colors.json")

DEFAULT_COLORS = [
    (255, 0, 0), (255, 105, 180), (255, 20, 147), (220, 20, 60), (255, 69, 0),
    (0, 255, 0), (0, 255, 0), (34, 139, 34), (0, 0, 255), (135, 206, 250),
    (65, 105, 225), (255, 255, 0), (255, 0, 255), (0, 255, 255),
    (255, 165, 0), (255, 215, 0), (128, 0, 128), (238, 130, 238), (255, 0, 255),
]

def load_colors():
    if not exists(DATA_DIR):
        makedirs(DATA_DIR)
    if exists(COLORS_FILE):
        try:
            with open(COLORS_FILE, 'r') as f:
                colors_data = json.load(f)
                return [tuple(c) for c in colors_data]
        except (json.JSONDecodeError, FileNotFoundError):
            return DEFAULT_COLORS
    return DEFAULT_COLORS

def save_colors(colors_list):
    if not exists(DATA_DIR):
        makedirs(DATA_DIR)
    with open(COLORS_FILE, 'w') as f:
        json.dump(colors_list, f)

colors = load_colors()

input_box_active = False
input_box_text = ""

input_box_rect = pygame.Rect(S_W // 2 - 150, S_H // 2 + - 90, 300, 40)
add_button_rect = pygame.Rect(S_W // 2 - 150, S_H // 2 - 40, 140, 40)
remove_button_rect = pygame.Rect(S_W // 2 + 10, S_H // 2 - 40, 140, 40)
reset_button_rect = pygame.Rect(S_W // 2 - 70, S_H // 2 + 10, 140, 40)

selected_color_index = -1
color_list_display_rect = pygame.Rect(S_W // 2 - 150, S_H // 2 + 60, 300, 200)
color_list_scroll_offset = 0
COLOR_ITEM_HEIGHT = 30

def get_color_from_input(text):
    text = text.strip()
    if text.startswith("#"):
        try:
            pg_color = pygame.Color(text)
            return (pg_color.r, pg_color.g, pg_color.b)
        except ValueError:
            return None
    else:
        try:
            rgb = [int(x.strip()) for x in text.split(',')]
            if len(rgb) == 3 and all(0 <= c <= 255 for c in rgb):
                return tuple(rgb)
            else:
                return None
        except ValueError:
            return None

color = pygame.Surface(dvd_img.get_size())
color.fill(random.choice(colors))


async def main_game_loop():
    global running, paused, direction, dvd_dir, dvd_vel, dvd_rect, input_box_active, input_box_text, selected_color_index, color_list_scroll_offset, colors, color

    running = True
    while running:
        dt = clock.tick()/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    if not paused:
                        save_colors(colors)
                if paused:
                    if input_box_active:
                        if event.key == pygame.K_BACKSPACE:
                            input_box_text = input_box_text[:-1]
                        elif event.key == pygame.K_RETURN:
                            new_color = get_color_from_input(input_box_text)
                            if new_color and new_color not in colors:
                                colors.append(new_color)
                                input_box_text = ""
                                save_colors(colors)
                            input_box_active = False
                        else:
                            input_box_text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if paused:
                    if event.button == 1:
                        if input_box_rect.collidepoint(event.pos):
                            input_box_active = True
                        else:
                            input_box_active = False

                        if add_button_rect.collidepoint(event.pos):
                            new_color = get_color_from_input(input_box_text)
                            if new_color and new_color not in colors:
                                colors.append(new_color)
                                input_box_text = ""
                                save_colors(colors)

                        if remove_button_rect.collidepoint(event.pos):
                            if selected_color_index != -1 and selected_color_index < len(colors):
                                del colors[selected_color_index]
                                selected_color_index = -1
                                save_colors(colors)

                        if reset_button_rect.collidepoint(event.pos):
                            colors = list(DEFAULT_COLORS)
                            selected_color_index = -1
                            save_colors(colors)

                        if color_list_display_rect.collidepoint(event.pos):
                            click_y_relative_to_list = event.pos[1] - color_list_display_rect.top + color_list_scroll_offset
                            index = click_y_relative_to_list // COLOR_ITEM_HEIGHT
                            if 0 <= index < len(colors):
                                selected_color_index = index
                            else:
                                selected_color_index = -1
                    
                    if event.button == 4:
                        color_list_scroll_offset = max(0, color_list_scroll_offset - COLOR_ITEM_HEIGHT)
                    elif event.button == 5:
                        max_scroll_offset = max(0, len(colors) * COLOR_ITEM_HEIGHT - color_list_display_rect.height)
                        color_list_scroll_offset = min(max_scroll_offset, color_list_scroll_offset + COLOR_ITEM_HEIGHT)

        screen.fill("#121313")
        if not paused:
            if dvd_rect.bottom >= S_H:
                dvd_rect.bottom = S_H
                dvd_dir.y*=-1
                color.fill(random.choice(colors))
            if dvd_rect.top <= 0:
                dvd_rect.top = 0
                dvd_dir.y*=-1
                color.fill(random.choice(colors))
            if dvd_rect.right >= S_W:
                dvd_rect.right = S_W
                dvd_dir.x*=-1
                color.fill(random.choice(colors))
            if dvd_rect.left <= 0:
                dvd_rect.left = 0
                dvd_dir.x*=-1
                color.fill(random.choice(colors))
            dvd_rect.center += dvd_dir * dvd_vel * dt
            screen.blit(color, dvd_rect)
            screen.blit(dvd_img, dvd_rect)
        else:
            pause_text = font.render("PAUSED", True, "white")
            pause_rect = pause_text.get_rect(center=(S_W // 2, S_H // 2 - 250))
            screen.blit(pause_text, pause_rect)

            resume_text = small_font.render("Press 'Esc' to Resume", True, "white")
            resume_rect = resume_text.get_rect(center=(S_W // 2, S_H // 2 - 200))
            screen.blit(resume_text, resume_rect)

            input_label = small_font.render("Add Color (RGB/Hex):", True, "white")
            screen.blit(input_label, (input_box_rect.x, input_box_rect.y - 30))
            pygame.draw.rect(screen, (255, 255, 255) if input_box_active else (200, 200, 200), input_box_rect, 2)
            text_surface = small_font.render(input_box_text, True, (255, 255, 255))
            text_rect_aligned = text_surface.get_rect(midleft=(input_box_rect.x + 5, input_box_rect.centery))
            screen.blit(text_surface, text_rect_aligned)

            pygame.draw.rect(screen, (0, 150, 0), add_button_rect)
            add_text = button_font.render("Add Color", True, "white")
            screen.blit(add_text, add_text.get_rect(center=add_button_rect.center))

            pygame.draw.rect(screen, (150, 0, 0), remove_button_rect)
            remove_text = button_font.render("Remove Color", True, "white")
            screen.blit(remove_text, remove_text.get_rect(center=remove_button_rect.center))

            pygame.draw.rect(screen, (100, 100, 200), reset_button_rect)
            reset_text = button_font.render("Reset Colors", True, "white")
            screen.blit(reset_text, reset_text.get_rect(center=reset_button_rect.center))

            pygame.draw.rect(screen, (50, 50, 50), color_list_display_rect)
            pygame.draw.rect(screen, (200, 200, 200), color_list_display_rect, 2)

            list_surface = pygame.Surface(color_list_display_rect.size, pygame.SRCALPHA)
            list_surface.fill((0,0,0,0))

            current_y_on_surface = 0
            for i, col in enumerate(colors):
                item_rect_on_surface = pygame.Rect(
                    5,
                    current_y_on_surface - color_list_scroll_offset,
                    color_list_display_rect.width - 10,
                    COLOR_ITEM_HEIGHT
                )

                if item_rect_on_surface.bottom > 0 and item_rect_on_surface.top < color_list_display_rect.height:
                    if i == selected_color_index:
                        pygame.draw.rect(list_surface, (70, 70, 100), item_rect_on_surface)

                    color_sample_rect_on_surface = pygame.Rect(item_rect_on_surface.x + 5, item_rect_on_surface.y + 5, 20, 20)
                    pygame.draw.rect(list_surface, col, color_sample_rect_on_surface)
                    pygame.draw.rect(list_surface, (255, 255, 255), color_sample_rect_on_surface, 1)

                    color_text = small_font.render(f"RGB: {col}", True, "white")
                    list_surface.blit(color_text, (item_rect_on_surface.x + 35, item_rect_on_surface.y + 5))

                current_y_on_surface += COLOR_ITEM_HEIGHT
            
            screen.blit(list_surface, color_list_display_rect.topleft)

        pygame.display.update()
        await asyncio.sleep(0)

if __name__ == '__main__':
    asyncio.run(main_game_loop())