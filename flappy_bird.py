import pygame
from pygame import *
from random import randint
import math

pygame.init()

win_w = 1200
win_h = 600
window = display.set_mode((win_w, win_h))
display.set_caption("Flappy Bird")
clock = time.Clock()

main_font = font.Font(None, 80)
med_font = font.Font(None, 55)
small_font = font.Font(None, 36)

bird_x = 150
bird_y = win_h // 2
bird_vy = 0
bird_angle = 0
wing_timer = 0

score = 0
best_score = 0
state = "menu"
death_timer = 0
ground_offset = 0

cloud1_x = 100
cloud1_y = 80
cloud2_x = 450
cloud2_y = 130
cloud3_x = 800
cloud3_y = 60

mount1_x = 0
mount2_x = 350
mount3_x = 700

pipes = []

def add_pipes(start_x):
    x = start_x
    for i in range(20):
        top_h = randint(70, 270)
        gap = 220
        pipes.append([x, top_h, top_h + gap, False])
        x += 370

add_pipes(win_w + 200)

def draw_bird(x, y, angle, wing):
    surf = Surface((72, 52), SRCALPHA)
    draw.ellipse(surf, (255, 185, 0), (8, 22, 22, 12))
    draw.ellipse(surf, (255, 210, 0), (2, 10, 56, 36))
    draw.circle(surf, (255, 230, 40), (50, 15), 14)
    draw.polygon(surf, (255, 140, 0), [(62, 13), (72, 17), (62, 21)])
    draw.polygon(surf, (220, 100, 0), [(62, 16), (72, 17), (62, 20)])
    draw.circle(surf, (20, 20, 20), (54, 10), 5)
    draw.circle(surf, (255, 255, 255), (56, 8), 2)
    rotated = transform.rotate(surf, -angle)
    window.blit(rotated, (x - rotated.get_width() // 2, y - rotated.get_height() // 2))

def draw_pipe(x, top_h, bot_y):
    pipe_color = (55, 160, 55)
    pipe_dark = (35, 110, 35)
    pipe_light = (85, 195, 85)
    pipe_w = 90
    cap_w = 108
    cap_h = 34
    cap_x = x - (cap_w - pipe_w) // 2

    draw.rect(window, pipe_color, (x + 5, 0, pipe_w - 10, top_h))
    draw.rect(window, pipe_light, (x + 10, 0, 12, top_h))
    draw.rect(window, pipe_dark, (x + pipe_w - 14, 0, 9, top_h))
    draw.rect(window, pipe_color, (cap_x, top_h - cap_h, cap_w, cap_h))
    draw.rect(window, pipe_light, (cap_x + 6, top_h - cap_h + 4, 16, cap_h - 8))
    draw.rect(window, pipe_dark, (cap_x + cap_w - 20, top_h - cap_h + 4, 13, cap_h - 8))

    bot_h = win_h - 50 - bot_y
    draw.rect(window, pipe_color, (x + 5, bot_y + cap_h, pipe_w - 10, bot_h))
    draw.rect(window, pipe_light, (x + 10, bot_y + cap_h, 12, bot_h))
    draw.rect(window, pipe_dark, (x + pipe_w - 14, bot_y + cap_h, 9, bot_h))
    draw.rect(window, pipe_color, (cap_x, bot_y, cap_w, cap_h))
    draw.rect(window, pipe_light, (cap_x + 6, bot_y + 4, 16, cap_h - 8))
    draw.rect(window, pipe_dark, (cap_x + cap_w - 20, bot_y + 4, 13, cap_h - 8))

def draw_cloud(x, y, w, h):
    surf = Surface((w, h), SRCALPHA)
    draw.ellipse(surf, (255, 255, 255, 210), (0, h // 2, int(w * 0.55), h // 2))
    draw.ellipse(surf, (255, 255, 255, 210), (int(w * 0.28), int(h * 0.12), int(w * 0.6), int(h * 0.75)))
    draw.ellipse(surf, (255, 255, 255, 210), (int(w * 0.6), int(h * 0.3), int(w * 0.4), int(h * 0.55)))
    window.blit(surf, (int(x), y))

def draw_mountain(x, y, w, h):
    surf = Surface((w, h), SRCALPHA)
    draw.polygon(surf, (140, 160, 200, 110), [(0, h), (w // 2, 0), (w, h)])
    draw.polygon(surf, (220, 230, 255, 150), [(w // 2 - 28, 38), (w // 2, 0), (w // 2 + 28, 38)])
    window.blit(surf, (int(x), y))

def draw_sky():
    for i in range(win_h):
        t = i / win_h
        r = int(95 + 85 * t)
        g = int(175 + 45 * t)
        b = 255
        draw.line(window, (r, g, b), (0, i), (win_w, i))

def draw_ground(offset):
    tile_w = 60
    draw.rect(window, (90, 185, 70), (0, win_h - 50, win_w, 30))
    draw.rect(window, (70, 155, 55), (0, win_h - 22, win_w, 22))
    ox = int(offset) % tile_w
    for x in range(-tile_w + ox, win_w + tile_w, tile_w):
        draw.rect(window, (75, 165, 60), (x, win_h - 48, 8, 4))
        draw.rect(window, (75, 165, 60), (x + 20, win_h - 44, 6, 3))
        draw.rect(window, (75, 165, 60), (x + 38, win_h - 47, 9, 4))

def draw_score():
    shadow = main_font.render(str(score), True, (0, 0, 0))
    txt = main_font.render(str(score), True, (255, 255, 255))
    cx = win_w // 2 - txt.get_width() // 2
    window.blit(shadow, (cx + 3, 23))
    window.blit(txt, (cx, 20))

def draw_menu():
    panel = Surface((500, 270), SRCALPHA)
    draw.rect(panel, (0, 0, 0, 140), (0, 0, 500, 270), border_radius=18)
    window.blit(panel, (win_w // 2 - 250, win_h // 2 - 155))

    t1 = main_font.render("FLAPPY BIRD", True, (255, 225, 0))
    t2 = small_font.render("Пробіл або W - стрибок", True, (255, 255, 255))
    t3 = small_font.render("Рекорд: " + str(best_score), True, (255, 200, 80))
    window.blit(t1, (win_w // 2 - t1.get_width() // 2, win_h // 2 - 135))
    window.blit(t2, (win_w // 2 - t2.get_width() // 2, win_h // 2 - 30))
    window.blit(t3, (win_w // 2 - t3.get_width() // 2, win_h // 2 + 15))

    btn_x = win_w // 2 - 110
    btn_y = win_h // 2 + 65
    draw.rect(window, (255, 200, 0), (btn_x, btn_y, 220, 52), border_radius=12)
    draw.rect(window, (190, 140, 0), (btn_x, btn_y, 220, 52), 3, border_radius=12)
    bt = med_font.render("ГРАТИ", True, (50, 30, 0))
    window.blit(bt, (btn_x + 110 - bt.get_width() // 2, btn_y + 26 - bt.get_height() // 2))

def draw_gameover():
    overlay = Surface((win_w, win_h), SRCALPHA)
    draw.rect(overlay, (0, 0, 0, 110), (0, 0, win_w, win_h))
    window.blit(overlay, (0, 0))

    panel = Surface((460, 290), SRCALPHA)
    draw.rect(panel, (0, 0, 0, 175), (0, 0, 460, 290), border_radius=18)
    window.blit(panel, (win_w // 2 - 230, win_h // 2 - 165))

    t1 = main_font.render("ГРА ЗАКІНЧЕНА", True, (255, 75, 75))
    t2 = med_font.render("Рахунок: " + str(score), True, (255, 255, 255))
    t3 = med_font.render("Рекорд: " + str(best_score), True, (255, 215, 55))
    window.blit(t1, (win_w // 2 - t1.get_width() // 2, win_h // 2 - 148))
    window.blit(t2, (win_w // 2 - t2.get_width() // 2, win_h // 2 - 55))
    window.blit(t3, (win_w // 2 - t3.get_width() // 2, win_h // 2 + 0))

    btn_x = win_w // 2 - 130
    btn_y = win_h // 2 + 60
    draw.rect(window, (75, 195, 115), (btn_x, btn_y, 260, 58), border_radius=13)
    draw.rect(window, (35, 135, 75), (btn_x, btn_y, 260, 58), 3, border_radius=13)
    bt = med_font.render("RESTART  (R)", True, (10, 40, 15))
    window.blit(bt, (btn_x + 130 - bt.get_width() // 2, btn_y + 29 - bt.get_height() // 2))

running = True
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

        if e.type == KEYDOWN:
            if e.key in (K_SPACE, K_w, K_UP):
                if state == "menu":
                    state = "play"
                    bird_y = win_h // 2
                    bird_vy = 0
                    score = 0
                    pipes.clear()
                    add_pipes(win_w + 200)
                elif state == "play":
                    bird_vy = -12
                elif state == "dead" and death_timer > 30:
                    state = "play"
                    bird_x = 150
                    bird_y = win_h // 2
                    bird_vy = 0
                    bird_angle = 0
                    score = 0
                    death_timer = 0
                    pipes.clear()
                    add_pipes(win_w + 200)

            if e.key == K_r and state == "dead" and death_timer > 30:
                state = "play"
                bird_x = 150
                bird_y = win_h // 2
                bird_vy = 0
                bird_angle = 0
                score = 0
                death_timer = 0
                pipes.clear()
                add_pipes(win_w + 200)

        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            if state == "menu":
                state = "play"
                bird_y = win_h // 2
                bird_vy = 0
                score = 0
                pipes.clear()
                add_pipes(win_w + 200)
            elif state == "dead" and death_timer > 30:
                state = "play"
                bird_x = 150
                bird_y = win_h // 2
                bird_vy = 0
                bird_angle = 0
                score = 0
                death_timer = 0
                pipes.clear()
                add_pipes(win_w + 200)

    wing_timer += 1

    if state == "play":
        bird_vy += 0.6
        bird_y += bird_vy
        bird_angle = max(-30, min(85, bird_vy * 4))

        ground_offset -= 5
        cloud1_x -= 0.4
        cloud2_x -= 0.6
        cloud3_x -= 0.5
        if cloud1_x < -170: cloud1_x = win_w + 50
        if cloud2_x < -130: cloud2_x = win_w + 50
        if cloud3_x < -150: cloud3_x = win_w + 50
        mount1_x -= 1.5
        mount2_x -= 1.5
        mount3_x -= 1.5
        if mount1_x < -330: mount1_x = win_w + 50
        if mount2_x < -330: mount2_x = win_w + 50
        if mount3_x < -330: mount3_x = win_w + 50

        for p in pipes:
            p[0] -= 5

            if not p[3] and p[0] + 90 < bird_x:
                p[3] = True
                score += 1

            hit_rect = Rect(bird_x - 16, bird_y - 14, 32, 28)
            top_rect = Rect(p[0], 0, 90, p[1])
            bot_rect = Rect(p[0], p[2], 90, win_h - p[2])
            if hit_rect.colliderect(top_rect) or hit_rect.colliderect(bot_rect):
                best_score = max(best_score, score)
                state = "dead"
                death_timer = 0

        if bird_y >= win_h - 70 or bird_y < -20:
            best_score = max(best_score, score)
            state = "dead"
            death_timer = 0

        if len(pipes) > 0 and pipes[-1][0] < win_w + 50:
            add_pipes(pipes[-1][0] + 370)

        for i in range(len(pipes) - 1, -1, -1):
            if pipes[i][0] < -200:
                pipes.pop(i)

    elif state == "dead":
        death_timer += 1
        bird_vy += 0.8
        bird_y += int(bird_vy)
        if bird_y > win_h - 75:
            bird_y = win_h - 75
        bird_angle = min(bird_angle + 5, 90)
        ground_offset -= 5
        cloud1_x -= 0.4
        cloud2_x -= 0.6
        cloud3_x -= 0.5
        if cloud1_x < -170: cloud1_x = win_w + 50
        if cloud2_x < -130: cloud2_x = win_w + 50
        if cloud3_x < -150: cloud3_x = win_w + 50

    elif state == "menu":
        ground_offset -= 1
        cloud1_x -= 0.2
        cloud2_x -= 0.3
        cloud3_x -= 0.25
        if cloud1_x < -170: cloud1_x = win_w + 50
        if cloud2_x < -130: cloud2_x = win_w + 50
        if cloud3_x < -150: cloud3_x = win_w + 50
        bird_y = win_h // 2 + int(math.sin(pygame.time.get_ticks() * 0.003) * 20)

    draw_sky()
    draw_mountain(mount1_x, win_h - 275, 320, 210)
    draw_mountain(mount2_x, win_h - 235, 280, 175)
    draw_mountain(mount3_x, win_h - 255, 300, 195)
    draw_cloud(cloud1_x, cloud1_y, 160, 80)
    draw_cloud(cloud2_x, cloud2_y, 130, 65)
    draw_cloud(cloud3_x, cloud3_y, 150, 75)

    if state != "menu":
        for p in pipes:
            draw_pipe(p[0], p[1], p[2])

    draw_ground(ground_offset)

    if state == "menu":
        draw_bird(200, bird_y, math.sin(pygame.time.get_ticks() * 0.003) * 12, wing_timer)
        draw_menu()
    elif state == "play":
        draw_bird(bird_x, int(bird_y), bird_angle, wing_timer)
        draw_score()
    elif state == "dead":
        for p in pipes:
            draw_pipe(p[0], p[1], p[2])
        draw_bird(bird_x, int(bird_y), bird_angle, wing_timer)
        draw_score()
        draw_gameover()

    display.update()
    clock.tick(60)

quit()