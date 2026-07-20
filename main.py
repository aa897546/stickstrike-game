import math
import random
import pygame

WIDTH, HEIGHT, FLOOR, FPS = 960, 540, 445, 60
WHITE, CYAN, PINK = (238, 247, 255), (99, 245, 255), (255, 77, 145)
PALETTE = [(99, 245, 255), (255, 77, 145), (255, 211, 78), (139, 255, 129), (181, 128, 255), (255, 126, 75)]
DIFFICULTIES = [("EASY", 0.010, 2.4, 6), ("NORMAL", 0.018, 3.4, 8), ("HARD", 0.030, 4.5, 10)]


class Fighter:
    def __init__(self, x, color, facing, style=None):
        self.spawn_x, self.color, self.spawn_facing = x, color, facing
        self.style = style or {"head": 0, "aura": True, "band": False}
        self.reset()

    def reset(self):
        self.x, self.y, self.vx, self.vy = float(self.spawn_x), float(FLOOR), 0.0, 0.0
        self.hp, self.facing, self.attack_timer = 100, self.spawn_facing, 0
        self.attack_hit, self.hurt_timer = False, 0

    @property
    def grounded(self): return self.y >= FLOOR

    def jump(self):
        if self.grounded and self.hurt_timer <= 0: self.vy = -13.5

    def attack(self):
        if self.attack_timer <= 0 and self.hurt_timer <= 0:
            self.attack_timer, self.attack_hit = 20, False

    def update(self):
        self.vy += 0.72; self.x += self.vx; self.y += self.vy; self.vx *= 0.76
        if self.y >= FLOOR: self.y, self.vy = FLOOR, 0
        self.x = max(55, min(WIDTH - 55, self.x))
        self.attack_timer, self.hurt_timer = max(0, self.attack_timer - 1), max(0, self.hurt_timer - 1)

    def try_hit(self, target, damage):
        if 6 < self.attack_timer < 13 and not self.attack_hit and abs(self.x-target.x) < 92 and abs(self.y-target.y) < 65:
            self.attack_hit = True; target.hp = max(0, target.hp-damage); target.hurt_timer = 12
            target.vx, target.vy = self.facing*8, -3.5

    def draw(self, surface, ticks, preview=False):
        x, y = int(self.x), int(self.y)
        stride = math.sin(ticks*.018)*13 if self.grounded and abs(self.vx)>.3 else 0
        lean = -self.facing*10 if self.hurt_timer else self.vx*.6
        progress = 1-abs(self.attack_timer-10)/10 if self.attack_timer else 0
        punch = max(0, progress)*43
        color = WHITE if self.hurt_timer and (ticks//60)%2 else self.color
        def pt(dx, dy): return int(x+dx*self.facing), int(y+dy)
        if self.style["aura"]:
            aura = pygame.Surface((150, 150), pygame.SRCALPHA)
            pygame.draw.circle(aura, (*self.color, 26), (75, 75), 55)
            surface.blit(aura, (x-75, y-125))
        head = pt(lean, -82)
        if self.style["head"] == 0:
            pygame.draw.circle(surface, (8,11,18), head, 16); pygame.draw.circle(surface, color, head, 16, 7)
        elif self.style["head"] == 1:
            pygame.draw.rect(surface, (8,11,18), (head[0]-15,head[1]-15,30,30), border_radius=3)
            pygame.draw.rect(surface, color, (head[0]-15,head[1]-15,30,30), 7, border_radius=3)
        else:
            pygame.draw.polygon(surface, (8,11,18), [(head[0],head[1]-19),(head[0]+18,head[1]+15),(head[0]-18,head[1]+15)])
            pygame.draw.polygon(surface, color, [(head[0],head[1]-19),(head[0]+18,head[1]+15),(head[0]-18,head[1]+15)], 7)
        if self.style["band"]:
            pygame.draw.line(surface, PINK, pt(lean-18,-85), pt(lean+18,-85), 5)
            pygame.draw.line(surface, PINK, pt(lean-17,-85), pt(lean-32,-75), 4)
        for a,b in [((lean,-65),(0,-20)),((lean-1,-55),(20+punch,-43-punch*.12)),((lean-2,-53),(-22,-34)),((0,-20),(20+stride,0)),((0,-20),(-18-stride,0))]:
            pygame.draw.line(surface, color, pt(*a), pt(*b), 8)


class Button:
    def __init__(self, rect, text, action): self.rect, self.text, self.action = pygame.Rect(rect), text, action
    def draw(self, screen, font, mouse):
        hover = self.rect.collidepoint(mouse)
        pygame.draw.rect(screen, (18,31,48) if hover else (12,20,33), self.rect, border_radius=5)
        pygame.draw.rect(screen, CYAN if hover else (47,69,94), self.rect, 2, border_radius=5)
        label = font.render(self.text, True, WHITE if hover else (184,201,219))
        screen.blit(label, label.get_rect(center=self.rect.center))


def background(screen):
    screen.fill((7,12,23))
    for y in range(HEIGHT):
        shade = int(9+y/HEIGHT*10); pygame.draw.line(screen,(shade,shade+3,shade+14),(0,y),(WIDTH,y))
    for x in range(0,WIDTH,48): pygame.draw.line(screen,(17,34,50),(x,0),(x,HEIGHT))
    for y in range(0,HEIGHT,48): pygame.draw.line(screen,(17,34,50),(0,y),(WIDTH,y))
    pygame.draw.circle(screen,(42,18,42),(WIDTH//2,225),132); pygame.draw.circle(screen,PINK,(WIDTH//2,225),88,3)
    pygame.draw.rect(screen,(5,7,13),(0,FLOOR+3,WIDTH,HEIGHT-FLOOR)); pygame.draw.line(screen,CYAN,(0,FLOOR+2),(WIDTH,FLOOR+2),4)


def centered(screen, font, text, y, color=WHITE):
    img=font.render(text,True,color); screen.blit(img,img.get_rect(center=(WIDTH//2,y)))


def hud(screen, player, enemy, font, small, wins, target):
    pygame.draw.rect(screen,(9,13,22),(0,0,WIDTH,78)); pygame.draw.line(screen,(34,48,71),(0,78),(WIDTH,78))
    screen.blit(small.render(f"PLAYER  {wins[0]}/{target}",True,player.color),(28,15))
    e=small.render(f"CPU  {wins[1]}/{target}",True,enemy.color); screen.blit(e,(WIDTH-28-e.get_width(),15))
    pygame.draw.rect(screen,(23,32,49),(28,42,365,17)); pygame.draw.rect(screen,player.color,(31,45,int(359*player.hp/100),11))
    pygame.draw.rect(screen,(23,32,49),(WIDTH-393,42,365,17)); ew=int(359*enemy.hp/100); pygame.draw.rect(screen,enemy.color,(WIDTH-31-ew,45,ew,11))
    inf=font.render("∞",True,WHITE); screen.blit(inf,inf.get_rect(center=(WIDTH//2,48)))


def main():
    pygame.init(); screen=pygame.display.set_mode((WIDTH,HEIGHT)); pygame.display.set_caption("STICKSTRIKE")
    clock=pygame.time.Clock(); title=pygame.font.SysFont("arialblack",68,bold=True); large=pygame.font.SysFont("arialblack",34,bold=True)
    font=pygame.font.SysFont("arial",22,bold=True); small=pygame.font.SysFont("consolas",14,bold=True)
    state, difficulty, rounds, color_index = "menu", 1, 2, 0
    style={"head":0,"aura":True,"band":False}; wins=[0,0]; round_done=False; result_timer=0
    player=Fighter(245,PALETTE[color_index],1,style); enemy=Fighter(715,PINK,-1,{"head":1,"aura":True,"band":False})

    def new_match():
        nonlocal wins, round_done, result_timer, player, enemy
        wins=[0,0]; round_done=False; result_timer=0
        player=Fighter(245,PALETTE[color_index],1,style); enemy=Fighter(715,PINK,-1,{"head":1,"aura":True,"band":False})

    running=True
    while running:
        mouse=pygame.mouse.get_pos(); click=None
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1: click=event.pos
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    state="pause" if state=="game" else ("game" if state=="pause" else "menu")
                if state=="game" and not round_done:
                    if event.key in (pygame.K_w,pygame.K_UP): player.jump()
                    if event.key in (pygame.K_j,pygame.K_SPACE): player.attack()

        background(screen)
        buttons=[]
        if state=="menu":
            centered(screen,title,"STICKSTRIKE",125); centered(screen,small,"NEON STICK FIGHTER",170,CYAN)
            buttons=[Button((350,220,260,52),"START GAME","start"),Button((350,286,260,52),"OPTIONS","options"),Button((350,352,260,52),"CUSTOMIZE","custom"),Button((350,418,260,52),"QUIT","quit")]
        elif state=="options":
            centered(screen,large,"OPTIONS",95); centered(screen,font,"Difficulty",180,(160,178,201))
            centered(screen,large,DIFFICULTIES[difficulty][0],222,CYAN)
            centered(screen,font,"Rounds to win",300,(160,178,201)); centered(screen,large,str(rounds),342,PINK)
            buttons=[Button((260,200,54,45),"<","diff-"),Button((646,200,54,45),">","diff+"),Button((350,375,115,45),"-","round-"),Button((495,375,115,45),"+","round+"),Button((350,455,260,45),"BACK","back")]
        elif state=="custom":
            centered(screen,large,"CUSTOMIZE FIGHTER",65)
            preview=Fighter(WIDTH//2,PALETTE[color_index],1,style); preview.y=330; preview.draw(screen,pygame.time.get_ticks(),True)
            centered(screen,font,"Color",370); 
            for i,c in enumerate(PALETTE):
                r=pygame.Rect(322+i*54,400,38,38); pygame.draw.circle(screen,c,r.center,16); pygame.draw.circle(screen,WHITE,r.center,19,3 if i==color_index else 1)
                if click and r.collidepoint(click): color_index=i
            head_names=["ROUND","SQUARE","TRIANGLE"]
            centered(screen,small,f"HEAD: {head_names[style['head']]}   AURA: {'ON' if style['aura'] else 'OFF'}   HEADBAND: {'ON' if style['band'] else 'OFF'}",475,(160,178,201))
            buttons=[Button((110,450,130,42),"HEAD","head"),Button((110,498,130,32),"AURA","aura"),Button((720,450,130,42),"HEADBAND","band"),Button((720,498,130,32),"BACK","back")]
        elif state in ("game","pause"):
            if state=="game" and not round_done:
                keys=pygame.key.get_pressed(); direction=int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT])
                player.vx=max(-6,min(6,player.vx+direction*.85)); gap=player.x-enemy.x; player.facing=1 if enemy.x>player.x else -1; enemy.facing=1 if gap>0 else -1
                chance,speed,damage=DIFFICULTIES[difficulty][1:]
                if abs(gap)>82 and enemy.hurt_timer<=0: enemy.vx=max(-speed,min(speed,enemy.vx+(1 if gap>0 else -1)*.42))
                if abs(gap)<86 and enemy.attack_timer<=0 and enemy.hurt_timer<=0 and random.random()<chance: enemy.attack()
                player.update(); enemy.update(); player.try_hit(enemy,10); enemy.try_hit(player,damage)
                if player.hp<=0 or enemy.hp<=0:
                    round_done=True; result_timer=pygame.time.get_ticks(); wins[0 if player.hp>0 else 1]+=1
            player.draw(screen,pygame.time.get_ticks()); enemy.draw(screen,pygame.time.get_ticks()); hud(screen,player,enemy,font,small,wins,rounds)
            screen.blit(small.render("A/D MOVE   W JUMP   J LIGHT ATTACK   ESC PAUSE",True,(135,150,173)),(22,HEIGHT-28))
            if round_done:
                match_over=max(wins)>=rounds; centered(screen,title,"YOU WIN" if wins[0]>wins[1] else "K.O.",260)
                buttons=[Button((350,330,260,48),"MAIN MENU" if match_over else "NEXT ROUND","menu" if match_over else "next")]
            if state=="pause":
                shade=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); shade.fill((2,5,10,210)); screen.blit(shade,(0,0)); centered(screen,large,"PAUSED",180)
                buttons=[Button((350,240,260,50),"RESUME","resume"),Button((350,305,260,50),"RESTART MATCH","restart"),Button((350,370,260,50),"MAIN MENU","menu")]

        for b in buttons:
            b.draw(screen,font,mouse)
            if click and b.rect.collidepoint(click):
                a=b.action
                if a=="start": new_match(); state="game"
                elif a=="options": state="options"
                elif a=="custom": state="custom"
                elif a=="back" or a=="menu": state="menu"
                elif a=="quit": running=False
                elif a=="diff-": difficulty=(difficulty-1)%len(DIFFICULTIES)
                elif a=="diff+": difficulty=(difficulty+1)%len(DIFFICULTIES)
                elif a=="round-": rounds=max(1,rounds-1)
                elif a=="round+": rounds=min(5,rounds+1)
                elif a=="head": style["head"]=(style["head"]+1)%3
                elif a=="aura": style["aura"]=not style["aura"]
                elif a=="band": style["band"]=not style["band"]
                elif a=="resume": state="game"
                elif a=="restart": new_match(); state="game"
                elif a=="next": player.reset(); enemy.reset(); round_done=False
        pygame.display.flip(); clock.tick(FPS)
    pygame.quit()

if __name__=="__main__": main()
