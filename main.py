import pgzrun
from pgzero.builtins import Rect, keyboard
import random

WIDTH, HEIGHT = 800, 600
current_screen = "menu"
volume_on = True
type_monstroides = [
    (["enemy_idle", "enemy_idle2"], ["enemy_walk", "enemy_walk2"]),
    (["enemy2_idle", "enemy2_idle2"], ["enemy2_walk", "enemy2_walk2"])
]

class MainCharac:
    def __init__(self, pos, anim_idle, anim_walk):
        self.pos = list(pos)
        self.anim_idle = anim_idle
        self.anim_walk = anim_walk
        self.frame = 0
        self.speed = 0 #tem como deixar essa parte mais compactada usando variaveis e virgulas e etc, mas ficaria bem grosseiro 
        self.vy = 0 
        self.walking = False
        self.on_floor = False
        self.time_anim = 0
        self.sprite = Actor(anim_idle[0], pos)
        self.direction = 1
        self.width, self.height = 50, 80

    def update(self, dt):
        self.time_anim += dt
        if self.time_anim >= 0.15:
            self.time_anim = 0
            anim = self.anim_walk if self.walking else self.anim_idle
            self.frame = (self.frame + 1) % len(anim)
            self.sprite.image = anim[self.frame]

        if self.walking:
            self.pos[0] += self.speed
            if self.speed > 0: self.direction = 1
            elif self.speed < 0: self.direction = -1

        self.vy += 0.8
        self.pos[1] += self.vy
        
        self.sprite.pos = self.pos
        self.sprite.flip_x = (self.direction == -1)

    def get_rect(self):
        return Rect(self.pos[0] - self.width/2, self.pos[1] - self.height/2, 
                   self.width, self.height)
    
    def draw(self):
        self.sprite.draw()

boboide = MainCharac(
    pos = (100, 500),
    anim_idle = ["main_idle", "main_idle2"],
    anim_walk = ["main_walk1", "main_walk2"]
) 

monstroides = [
    MainCharac((300 + i * 200, 500), *type_monstroides[i % 2])
    for i in range(2)
]
for m in monstroides:
    m.speed = random.choice([-1.5, 1.5])

buttons = {
    "START": Rect(300, 200, 200, 40),
    "som": Rect(300, 260, 200, 40),
    "sair": Rect(300, 320, 200, 40),
}

platform_rects = [
    Rect(0, 550, 800, 50),
    Rect(200, 450, 150, 20),
    Rect(500, 350, 150, 20)
]

def handle_collision(char, platforms):
    char.on_floor = False
    char_rect = char.get_rect()
    
    for platform in platforms:
        if char_rect.colliderect(platform):

            if char.vy >= 0 and char_rect.bottom > platform.top:
                char.pos[1] = platform.top - char.height/2 + 1
                char.vy = 0
                char.on_floor = True
                

            elif char.vy < 0 and char_rect.top < platform.bottom:
                char.pos[1] = platform.bottom + char.height/2
                char.vy = 0

def update_game(dt):
    global current_screen
    
    boboide.walking = keyboard.left or keyboard.right
    boboide.speed = 3 if keyboard.right else -3 if keyboard.left else 0
    
    if keyboard.space and boboide.on_floor:
        boboide.vy = -15
        if volume_on: sounds.jump.play()
    boboide.update(dt)
    
    if boboide.pos[0] < 20:
        boboide.pos[0] = 20
    elif boboide.pos[0] > WIDTH - 20:
        boboide.pos[0] = WIDTH - 20
    
    handle_collision(boboide, platform_rects)
    
    for monstroide in monstroides:
        monstroide.walking = True
        if monstroide.pos[0] < 50 or monstroide.pos[0] > WIDTH - 50:
            monstroide.speed *= -1
        
        monstroide.update(dt)
        handle_collision(monstroide, platform_rects)
        
        if boboide.get_rect().colliderect(monstroide.get_rect()):
            if volume_on: sounds.game_over.play()
            music.stop()
            current_screen = "end"
            break

def draw_game():
    screen.blit("cenary", (0, 0))
    for platform in platform_rects:
        screen.draw.filled_rect(platform, (70, 130, 200))
    
    boboide.draw()
    for monstroide in monstroides:
        monstroide.draw()

def reset_game():
    boboide.pos = [100, 500]
    boboide.vy = 0
    
    for i, monstroide in enumerate(monstroides):
        monstroide.pos = [300 + i * 200, 500]
        monstroide.speed = random.choice([-1.5, 1.5])

def draw_menu():
    screen.fill((255, 228, 132))
    screen.draw.text("As aventuras do Boboide", center = (400, 100), fontsize = 40, color = "black")
    
    for texto, ret in buttons.items():
        screen.draw.filled_rect(ret, (255, 153, 51))
        screen.draw.text(texto.upper(), center = ret.center, fontsize = 30, color = "white")
    
    if volume_on:
        screen.draw.text("Volume: ligadasso", center = (400, 400), fontsize = 20, color = (255, 102, 0))
    else:
        screen.draw.text("Volume: desligadasso", center = (400, 400), fontsize = 20, color = (20, 0, 0))

def draw_end():
    screen.fill((20, 0, 0))
    screen.draw.text("VOCÊ FOI BOBOIDE DEMAIS.", center = (400, 250), fontsize = 60, color = (255, 102, 0))
    screen.draw.text("Clique para recomeçar", center = (400, 350), fontsize = 30, color = (255, 228, 132))

def stop_all_sounds():
    music.stop()
    sounds.jump.stop()
    sounds.game_over.stop()

def update(dt):
    if current_screen == "game":
        update_game(dt)

def draw():
    if current_screen == "menu": draw_menu()
    elif current_screen == "game": draw_game()
    elif current_screen == "end": draw_end()

def on_mouse_down(pos):
    global current_screen, volume_on
    
    if current_screen == "menu":
        if buttons["START"].collidepoint(pos):
            current_screen = "game"
            reset_game()
            if volume_on: music.play("musica")
        elif buttons["som"].collidepoint(pos):
            volume_on = not volume_on
            if volume_on:
                music.play("musica")
            else:
                stop_all_sounds()
        elif buttons["sair"].collidepoint(pos):
            exit()
    
    elif current_screen == "end":
        current_screen = "menu"

music.set_volume(0.3)
sounds.game_over.set_volume(0.5)
sounds.jump.set_volume(0.3)
pgzrun.go()