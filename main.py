import math
import random
import pygame

WIDTH, HEIGHT, FLOOR, FPS = 960, 540, 445, 60
WHITE, CYAN, PINK, GOLD = (238, 247, 255), (99, 245, 255), (255, 77, 145), (255, 211, 78)
PALETTE = [CYAN, PINK, GOLD, (139, 255, 129), (181, 128, 255), (255, 126, 75)]
DIFFICULTIES = [("EASY", .010, 2.4, 6), ("NORMAL", .018, 3.4, 8), ("HARD", .030, 4.5, 10)]
LEVELS = [
    {"name": "NEON DOJO", "enemies": 1, "time": 75, "target": 700, "color": CYAN},
    {"name": "ROOFTOP RUSH", "enemies": 2, "time": 90, "target": 1500, "color": GOLD},
    {"name": "VOID CHAMPION", "enemies": 3, "time": 110, "target": 2600, "color": PINK},
]
WEAPONS = {
    "BAT": {"damage": 17, "range": 112, "uses": 7, "color": GOLD},
    "SWORD": {"damage": 22, "range": 132, "uses": 5, "color": CYAN},
    "HAMMER": {"damage": 29, "range": 104, "uses": 3, "color": PINK},
}
MOVES = {
    "LP": {"damage": 8, "range": 86, "duration": 16, "active": (5, 10), "knock": 6, "meter": 7},
    "HP": {"damage": 16, "range": 98, "duration": 27, "active": (9, 16), "knock": 11, "meter": 12},
    "LK": {"damage": 11, "range": 105, "duration": 20, "active": (6, 12), "knock": 8, "meter": 9},
    "HK": {"damage": 20, "range": 124, "duration": 31, "active": (11, 18), "knock": 14, "meter": 14},
    "ULT": {"damage": 38, "range": 175, "duration": 42, "active": (14, 25), "knock": 20, "meter": 0},
}
COMBOS = {
    ("LP", "LP", "HP"): ("RAPID BREAK", 8),
    ("LK", "LK", "HK"): ("CYCLONE KICK", 10),
    ("LP", "LK", "HP"): ("NEON FINISH", 12),
}


class WeaponPickup:
    def __init__(self, x, kind):
        self.x, self.y, self.kind = float(x), FLOOR - 13, kind
        self.phase = random.random() * math.tau

    def draw(self, surface, ticks, font):
        y = int(self.y + math.sin(ticks * .006 + self.phase) * 5)
        color = WEAPONS[self.kind]["color"]
        pygame.draw.circle(surface, (*color, 30), (int(self.x), y), 25)
        pygame.draw.line(surface, color, (int(self.x) - 14, y + 8), (int(self.x) + 14, y - 10), 7)
        label = font.render(self.kind, True, color)
        surface.blit(label, label.get_rect(center=(int(self.x), y - 28)))


class Fighter:
    def __init__(self, x, color, facing, style=None):
        self.spawn_x, self.color, self.spawn_facing = x, color, facing
        self.style = style or {"head": 0, "aura": True, "band": False}
        self.reset()

    def reset(self):
        self.x, self.y, self.vx, self.vy = float(self.spawn_x), float(FLOOR), 0.0, 0.0
        self.hp, self.facing, self.attack_timer = 100, self.spawn_facing, 0
        self.attack_hit, self.hurt_timer = False, 0
        self.weapon, self.weapon_uses = None, 0
        self.action, self.guard = None, False
        self.ultimate, self.combo_bonus = 0, 0
        self.combo_name, self.combo_display = "", 0
        self.combo_buffer, self.combo_timer = [], 0

    @property
    def grounded(self): return self.y >= FLOOR

    def jump(self):
        if self.grounded and self.hurt_timer <= 0: self.vy = -13.5

    def attack(self, move="LP"):
        if move == "ULT" and self.ultimate < 100: return False
        if self.attack_timer <= 0 and self.hurt_timer <= 0:
            data = MOVES[move]
            self.action, self.attack_timer, self.attack_hit = move, data["duration"], False
            self.guard = False
            if move == "ULT": self.ultimate = 0
            else:
                self.combo_buffer.append(move); self.combo_buffer = self.combo_buffer[-3:]; self.combo_timer = 45
                key = tuple(self.combo_buffer)
                if key in COMBOS:
                    self.combo_name, self.combo_bonus = COMBOS[key]
                    self.combo_display, self.combo_buffer = 75, []
            return True
        return False

    def pickup(self, item):
        self.weapon = item.kind
        self.weapon_uses = WEAPONS[item.kind]["uses"]

    def update(self):
        self.vy += .72; self.x += self.vx; self.y += self.vy; self.vx *= .76
        if self.y >= FLOOR: self.y, self.vy = FLOOR, 0
        self.x = max(55, min(WIDTH - 55, self.x))
        self.attack_timer = max(0, self.attack_timer - 1)
        self.hurt_timer = max(0, self.hurt_timer - 1)
        self.combo_timer = max(0, self.combo_timer - 1); self.combo_display = max(0, self.combo_display - 1)
        if self.combo_timer == 0: self.combo_buffer = []
        if self.attack_timer == 0: self.action = None

    def try_hit(self, target, base_damage):
        if not self.action: return 0
        move = MOVES[self.action]
        weapon = WEAPONS.get(self.weapon, {})
        attack_range = max(move["range"], weapon.get("range", 0))
        damage = move["damage"] + self.combo_bonus
        if self.weapon and self.action != "ULT": damage += max(0, weapon["damage"] - 10)
        elapsed = move["duration"] - self.attack_timer
        active = move["active"][0] <= elapsed <= move["active"][1]
        if active and not self.attack_hit and abs(self.x-target.x) < attack_range and abs(self.y-target.y) < 65:
            self.attack_hit = True
            blocked = target.guard and target.hurt_timer <= 0 and target.facing == -self.facing
            actual = max(1, int(damage * .22)) if blocked else damage
            target.hp = max(0, target.hp-actual); target.hurt_timer = 4 if blocked else 12
            target.vx, target.vy = self.facing * (3 if blocked else move["knock"]), -1 if blocked else -4
            self.ultimate = min(100, self.ultimate + move["meter"] + (4 if blocked else 8))
            target.ultimate = min(100, target.ultimate + actual * .7)
            if self.weapon:
                self.weapon_uses -= 1
                if self.weapon_uses <= 0: self.weapon = None
            self.combo_bonus = 0
            return actual
        return 0

    def draw(self, surface, ticks):
        x, y = int(self.x), int(self.y)
        stride = math.sin(ticks*.018)*13 if self.grounded and abs(self.vx)>.3 else 0
        lean = -self.facing*10 if self.hurt_timer else self.vx*.6
        progress = math.sin(math.pi * (1-self.attack_timer/max(1,MOVES.get(self.action,{"duration":1})["duration"]))) if self.attack_timer else 0
        punch = max(0, progress) * (55 if self.weapon else 43)
        color = WHITE if self.hurt_timer and (ticks//60)%2 else self.color
        def pt(dx, dy): return int(x+dx*self.facing), int(y+dy)
        if self.style["aura"]:
            aura = pygame.Surface((150,150), pygame.SRCALPHA)
            pygame.draw.circle(aura, (*self.color, 26), (75,75), 55); surface.blit(aura,(x-75,y-125))
        if self.action == "ULT":
            pygame.draw.circle(surface, WHITE, (x,y-55), 72, 3); pygame.draw.circle(surface, self.color, (x,y-55), 62, 5)
        head = pt(lean,-82)
        if self.style["head"] == 0:
            pygame.draw.circle(surface,(8,11,18),head,16); pygame.draw.circle(surface,color,head,16,7)
        elif self.style["head"] == 1:
            pygame.draw.rect(surface,(8,11,18),(head[0]-15,head[1]-15,30,30),border_radius=3); pygame.draw.rect(surface,color,(head[0]-15,head[1]-15,30,30),7,border_radius=3)
        else:
            pts=[(head[0],head[1]-19),(head[0]+18,head[1]+15),(head[0]-18,head[1]+15)]
            pygame.draw.polygon(surface,(8,11,18),pts); pygame.draw.polygon(surface,color,pts,7)
        if self.style["band"]:
            pygame.draw.line(surface,PINK,pt(lean-18,-85),pt(lean+18,-85),5); pygame.draw.line(surface,PINK,pt(lean-17,-85),pt(lean-32,-75),4)
        is_kick = self.action in ("LK","HK")
        is_heavy = self.action in ("HP","HK","ULT")
        arm_reach = punch * (1.35 if is_heavy else 1)
        kick_reach = max(0,progress) * (78 if is_heavy else 58) if is_kick else stride
        hand = pt(20+arm_reach,-43-arm_reach*.12)
        guard_arm = (8,-68) if self.guard else (20+arm_reach,-43-arm_reach*.12)
        for a,b in [((lean,-65),(0,-20)),((lean-1,-55),guard_arm),((lean-2,-53),(-8,-70) if self.guard else (-22,-34)),((0,-20),(20+kick_reach,-34 if is_kick else 0)),((0,-20),(-18-stride,0))]:
            pygame.draw.line(surface,color,pt(*a),pt(*b),8)
        if self.weapon:
            wc=WEAPONS[self.weapon]["color"]
            pygame.draw.line(surface,wc,hand,(hand[0]+34*self.facing,hand[1]-24),7)


class Button:
    def __init__(self, rect, text, action): self.rect, self.text, self.action = pygame.Rect(rect), text, action
    def draw(self, screen, font, mouse):
        hover=self.rect.collidepoint(mouse)
        pygame.draw.rect(screen,(18,31,48) if hover else (12,20,33),self.rect,border_radius=5)
        pygame.draw.rect(screen,CYAN if hover else (47,69,94),self.rect,2,border_radius=5)
        label=font.render(self.text,True,WHITE if hover else (184,201,219)); screen.blit(label,label.get_rect(center=self.rect.center))


def background(screen, accent=CYAN):
    screen.fill((7,12,23))
    for y in range(HEIGHT):
        shade=int(9+y/HEIGHT*10); pygame.draw.line(screen,(shade,shade+3,shade+14),(0,y),(WIDTH,y))
    for x in range(0,WIDTH,48): pygame.draw.line(screen,(17,34,50),(x,0),(x,HEIGHT))
    for y in range(0,HEIGHT,48): pygame.draw.line(screen,(17,34,50),(0,y),(WIDTH,y))
    pygame.draw.circle(screen,(42,18,42),(WIDTH//2,225),132); pygame.draw.circle(screen,accent,(WIDTH//2,225),88,3)
    pygame.draw.rect(screen,(5,7,13),(0,FLOOR+3,WIDTH,HEIGHT-FLOOR)); pygame.draw.line(screen,accent,(0,FLOOR+2),(WIDTH,FLOOR+2),4)


def centered(screen,font,text,y,color=WHITE):
    img=font.render(text,True,color); screen.blit(img,img.get_rect(center=(WIDTH//2,y)))


def draw_star(surface, center, radius, filled):
    pts=[]
    for i in range(10):
        angle=-math.pi/2+i*math.pi/5; r=radius if i%2==0 else radius*.45
        pts.append((center[0]+math.cos(angle)*r,center[1]+math.sin(angle)*r))
    pygame.draw.polygon(surface,GOLD if filled else (48,55,70),pts)
    pygame.draw.polygon(surface,GOLD,pts,2)


def hud(screen,player,enemy,font,small,score,time_left,level):
    pygame.draw.rect(screen,(9,13,22),(0,0,WIDTH,78)); pygame.draw.line(screen,(34,48,71),(0,78),(WIDTH,78))
    screen.blit(small.render(f"SCORE {score:05d}",True,GOLD),(28,13))
    screen.blit(small.render(f"LEVEL {level+1}: {LEVELS[level]['name']}",True,LEVELS[level]["color"]),(28,35))
    weapon=f"{player.weapon} x{player.weapon_uses}" if player.weapon else "UNARMED"
    screen.blit(small.render(weapon,True,player.color),(28,56))
    pygame.draw.rect(screen,(23,32,49),(245,50,255,9)); pygame.draw.rect(screen,GOLD,(248,53,int(249*player.ultimate/100),3))
    pygame.draw.rect(screen,(23,32,49),(245,25,255,17)); pygame.draw.rect(screen,player.color,(248,28,int(249*player.hp/100),11))
    pygame.draw.rect(screen,(23,32,49),(WIDTH-355,25,255,17)); ew=int(249*enemy.hp/100); pygame.draw.rect(screen,enemy.color,(WIDTH-103-ew,28,ew,11))
    timer=font.render(str(max(0,int(time_left))),True,WHITE); screen.blit(timer,timer.get_rect(center=(WIDTH//2,58)))


def main():
    pygame.init(); screen=pygame.display.set_mode((WIDTH,HEIGHT)); pygame.display.set_caption("STICKSTRIKE")
    clock=pygame.time.Clock(); title=pygame.font.SysFont("arialblack",68,bold=True); large=pygame.font.SysFont("arialblack",34,bold=True)
    font=pygame.font.SysFont("arial",22,bold=True); small=pygame.font.SysFont("consolas",14,bold=True)
    state,difficulty,rounds,color_index,selected_level="menu",1,2,0,0
    style={"head":0,"aura":True,"band":False}; wins=[0,0]; round_done=False
    score,stars,level_start,enemies_left=0,0,0,0; pickups=[]; next_drop=0; level_complete=False
    player=Fighter(245,PALETTE[color_index],1,style); enemy=Fighter(715,PINK,-1,{"head":1,"aura":True,"band":False})

    def new_match():
        nonlocal wins,round_done,player,enemy,enemies_left
        wins=[0,0]; round_done=False; enemies_left=0
        player=Fighter(245,PALETTE[color_index],1,style); enemy=Fighter(715,PINK,-1,{"head":1,"aura":True,"band":False})

    def new_level():
        nonlocal player,enemy,score,stars,level_start,enemies_left,pickups,next_drop,level_complete,round_done
        cfg=LEVELS[selected_level]; player=Fighter(180,PALETTE[color_index],1,style)
        enemy=Fighter(750,PINK,-1,{"head":(selected_level+1)%3,"aura":True,"band":selected_level==2})
        score,stars,level_start,enemies_left=0,0,pygame.time.get_ticks(),cfg["enemies"]
        pickups=[WeaponPickup(480,random.choice(list(WEAPONS)))]; next_drop=pygame.time.get_ticks()+9000
        level_complete=False; round_done=False

    running=True
    while running:
        mouse=pygame.mouse.get_pos(); click=None; pickup_pressed=False
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1: click=event.pos
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: state="pause" if state in ("game","level_game") else ("level_game" if state=="pause" and enemies_left else "game" if state=="pause" else "menu")
                if state in ("game","level_game") and not round_done and not level_complete:
                    if event.key in (pygame.K_w,pygame.K_UP): player.jump()
                    if event.key in (pygame.K_j,pygame.K_SPACE): player.attack("LP")
                    if event.key==pygame.K_k: player.attack("HP")
                    if event.key==pygame.K_u: player.attack("LK")
                    if event.key==pygame.K_i: player.attack("HK")
                    if event.key==pygame.K_o: player.attack("ULT")
                    if event.key in (pygame.K_e,pygame.K_DOWN): pickup_pressed=True

        accent=LEVELS[selected_level]["color"] if state in ("levels","level_game","level_result") else CYAN
        background(screen,accent); buttons=[]
        if state=="menu":
            centered(screen,title,"STICKSTRIKE",105); centered(screen,small,"NEON STICK FIGHTER",150,CYAN)
            buttons=[Button((350,190,260,48),"LEVEL MODE","levels"),Button((350,248,260,48),"ARCADE FIGHT","start"),Button((350,306,260,48),"OPTIONS","options"),Button((350,364,260,48),"CUSTOMIZE","custom"),Button((350,422,260,48),"QUIT","quit")]
        elif state=="levels":
            centered(screen,large,"SELECT LEVEL",62)
            for i,cfg in enumerate(LEVELS):
                r=pygame.Rect(135+i*235,135,220,235); selected=i==selected_level
                pygame.draw.rect(screen,(18,28,44) if selected else (10,17,29),r,border_radius=8); pygame.draw.rect(screen,cfg["color"] if selected else (48,61,81),r,3,border_radius=8)
                centered_x=r.centerx; n=large.render(str(i+1),True,cfg["color"]); screen.blit(n,n.get_rect(center=(centered_x,180)))
                name=small.render(cfg["name"],True,WHITE); screen.blit(name,name.get_rect(center=(centered_x,225)))
                info=small.render(f"{cfg['enemies']} ENEMIES",True,(150,166,185)); screen.blit(info,info.get_rect(center=(centered_x,270)))
                target=small.render(f"3 STAR: {cfg['target']}",True,GOLD); screen.blit(target,target.get_rect(center=(centered_x,305)))
                if click and r.collidepoint(click): selected_level=i
            buttons=[Button((350,400,260,48),"START LEVEL","level_start"),Button((350,460,260,42),"BACK","menu")]
        elif state=="options":
            centered(screen,large,"OPTIONS",95); centered(screen,font,"Difficulty",180,(160,178,201)); centered(screen,large,DIFFICULTIES[difficulty][0],222,CYAN)
            centered(screen,font,"Rounds to win",300,(160,178,201)); centered(screen,large,str(rounds),342,PINK)
            buttons=[Button((260,200,54,45),"<","diff-"),Button((646,200,54,45),">","diff+"),Button((350,375,115,45),"-","round-"),Button((495,375,115,45),"+","round+"),Button((350,455,260,45),"BACK","menu")]
        elif state=="custom":
            centered(screen,large,"CUSTOMIZE FIGHTER",65); preview=Fighter(WIDTH//2,PALETTE[color_index],1,style); preview.y=330; preview.draw(screen,pygame.time.get_ticks())
            centered(screen,font,"Color",370)
            for i,c in enumerate(PALETTE):
                r=pygame.Rect(322+i*54,400,38,38); pygame.draw.circle(screen,c,r.center,16); pygame.draw.circle(screen,WHITE,r.center,19,3 if i==color_index else 1)
                if click and r.collidepoint(click): color_index=i
            buttons=[Button((110,450,130,42),"HEAD","head"),Button((110,498,130,32),"AURA","aura"),Button((720,450,130,42),"HEADBAND","band"),Button((720,498,130,32),"BACK","menu")]
        elif state in ("game","level_game","pause"):
            level_mode=state=="level_game" or (state=="pause" and enemies_left>0)
            if state!="pause" and not round_done and not level_complete:
                keys=pygame.key.get_pressed(); direction=int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT])
                player.guard=bool(keys[pygame.K_l] or keys[pygame.K_RSHIFT]) and player.attack_timer<=0 and player.hurt_timer<=0
                player.vx=max(-6,min(6,player.vx+direction*.85)); gap=player.x-enemy.x; player.facing=1 if enemy.x>player.x else -1; enemy.facing=1 if gap>0 else -1
                chance,speed,damage=DIFFICULTIES[difficulty][1:]
                if level_mode: speed+=selected_level*.45; damage+=selected_level*2
                if abs(gap)>82 and enemy.hurt_timer<=0: enemy.vx=max(-speed,min(speed,enemy.vx+(1 if gap>0 else -1)*.42))
                enemy.guard=enemy.attack_timer<=0 and enemy.hurt_timer<=0 and player.attack_timer>0 and random.random()<(.06+selected_level*.02 if level_mode else .05)
                if abs(gap)<125 and enemy.attack_timer<=0 and enemy.hurt_timer<=0 and not enemy.guard and random.random()<chance:
                    if enemy.ultimate>=100 and random.random()<.45: enemy.attack("ULT")
                    else: enemy.attack(random.choices(["LP","HP","LK","HK"],[4,2,3,1])[0])
                player.update(); enemy.update(); dealt=player.try_hit(enemy,10); enemy.try_hit(player,damage)
                if dealt: score+=dealt*6+(40 if player.weapon else 0)
                if level_mode:
                    now=pygame.time.get_ticks(); time_left=LEVELS[selected_level]["time"]-(now-level_start)/1000
                    if now>=next_drop and len(pickups)<2: pickups.append(WeaponPickup(random.randint(180,780),random.choice(list(WEAPONS)))); next_drop=now+random.randint(8000,12000)
                    if pickup_pressed:
                        for item in pickups[:]:
                            if abs(player.x-item.x)<55: player.pickup(item); pickups.remove(item); score+=75; break
                    if enemy.hp<=0:
                        score+=300+int(max(0,time_left)*5); enemies_left-=1
                        if enemies_left<=0:
                            level_complete=True; ratio=score/LEVELS[selected_level]["target"]; stars=3 if ratio>=1 else 2 if ratio>=.6 else 1
                        else:
                            enemy=Fighter(760,PINK,-1,{"head":random.randrange(3),"aura":True,"band":selected_level==2}); player.hp=min(100,player.hp+25)
                    if player.hp<=0 or time_left<=0: level_complete=True; stars=1
                elif player.hp<=0 or enemy.hp<=0:
                    round_done=True; wins[0 if player.hp>0 else 1]+=1
            if level_mode:
                time_left=LEVELS[selected_level]["time"]-(pygame.time.get_ticks()-level_start)/1000
                for item in pickups: item.draw(screen,pygame.time.get_ticks(),small)
                hud(screen,player,enemy,font,small,score,time_left,selected_level)
            player.draw(screen,pygame.time.get_ticks()); enemy.draw(screen,pygame.time.get_ticks())
            help_text="J/K PUNCH  U/I KICK  L GUARD  O ULT  E PICKUP" if level_mode else "J/K PUNCH  U/I KICK  L GUARD  O ULT"
            screen.blit(small.render(help_text,True,(135,150,173)),(22,HEIGHT-28))
            if player.combo_display:
                centered(screen,large,player.combo_name,118,GOLD)
            if player.ultimate>=100:
                ready=small.render("ULTIMATE READY [O]",True,GOLD); screen.blit(ready,ready.get_rect(center=(WIDTH//2,92)))
            if round_done:
                match_over=max(wins)>=rounds; centered(screen,title,"YOU WIN" if wins[0]>wins[1] else "K.O.",260); buttons=[Button((350,330,260,48),"MAIN MENU" if match_over else "NEXT ROUND","menu" if match_over else "next")]
            if level_complete: state="level_result"
            if state=="pause":
                shade=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); shade.fill((2,5,10,210)); screen.blit(shade,(0,0)); centered(screen,large,"PAUSED",180)
                buttons=[Button((350,240,260,50),"RESUME","resume_level" if level_mode else "resume"),Button((350,305,260,50),"RESTART","level_start" if level_mode else "restart"),Button((350,370,260,50),"MAIN MENU","menu")]
        elif state=="level_result":
            centered(screen,large,"LEVEL COMPLETE" if player.hp>0 else "MISSION FAILED",110,accent)
            centered(screen,font,LEVELS[selected_level]["name"],155); centered(screen,large,f"SCORE {score}",225,GOLD)
            for i in range(3): draw_star(screen,(WIDTH//2-80+i*80,300),30,i<stars)
            target=LEVELS[selected_level]["target"]; centered(screen,small,f"1 STAR: COMPLETE   2 STARS: {int(target*.6)}   3 STARS: {target}",355,(156,171,190))
            buttons=[Button((350,400,260,48),"RETRY LEVEL","level_start"),Button((350,460,260,42),"LEVEL SELECT","levels")]

        for b in buttons:
            b.draw(screen,font,mouse)
            if click and b.rect.collidepoint(click):
                a=b.action
                if a=="start": new_match(); state="game"
                elif a=="levels": state="levels"
                elif a=="level_start": new_level(); state="level_game"
                elif a=="options": state="options"
                elif a=="custom": state="custom"
                elif a=="menu": state="menu"
                elif a=="quit": running=False
                elif a=="diff-": difficulty=(difficulty-1)%3
                elif a=="diff+": difficulty=(difficulty+1)%3
                elif a=="round-": rounds=max(1,rounds-1)
                elif a=="round+": rounds=min(5,rounds+1)
                elif a=="head": style["head"]=(style["head"]+1)%3
                elif a=="aura": style["aura"]=not style["aura"]
                elif a=="band": style["band"]=not style["band"]
                elif a=="resume": state="game"
                elif a=="resume_level": state="level_game"
                elif a=="restart": new_match(); state="game"
                elif a=="next": player.reset(); enemy.reset(); round_done=False
        pygame.display.flip(); clock.tick(FPS)
    pygame.quit()

if __name__=="__main__": main()
