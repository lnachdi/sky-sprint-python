import os
import csv


add_library('minim')

#Variables for Menu Screen
APP_STATE = "MENU"
CHOSEN_SKIN = "player.png"
LEVEL_COMPLETE = "LEVEL_COMPLETE"

PATH = os.getcwd()


SCREEN_W = 800
SCREEN_H = 450

#Standard Dimensions of objects in Game
TILE_W = 40
TILE_H = 40

VISIBLE_LEFT= -100
VISIBLE_RIGHT = SCREEN_W +200

# will be updated after loading grid
GROUND_Y = SCREEN_H - 80

# global images
IMG_PLAYER = None
IMG_BLOCK  = None
IMG_SPIKE  = None
IMG_MINI   = None
IMG_BG     = None
IMG_GROUND= None
IMG_JUMPPAD = None
IMG_PLATFORM = None
IMG_SHORTSPIKE = None
IMG_UDSPIKE = None
IMG_CHAIN = None
IMG_STEP = None
IMG_LEFTSPIKE=None
IMG_PORTAL = None
IMG_SHIP = None


game = None
myFont=None
IMG_TUTORIAL = None
minim = None
music = None



#BASE OBJECT CLASSES

class Ground:
    def __init__(self, img, h):
        self.x = 0
        self.y = SCREEN_H -h
        self.w = SCREEN_W *2
        self.h = h
        self.img = img
    
    def update(self):
        self.x -= game.scroll_speed
        if self.x <= - SCREEN_W:
            self.x =0
    def draw(self):
        image(self.img, self.x, self.y,self.w,self.h)

class Platform:
   
    def __init__(self, x, y, w, h, img):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.img = img
    
    
    def update(self):
        self.x -=game.scroll_speed
    
        
    def draw(self):
        image(self.img, self.x, self.y, self.w, self.h) 
        
    def collide(self, player):
        return (player.x + player.img_w > self.x and player.x < self.x +self.w and player.y + player.img_h > self.y and player.y < self.y + self.h)

#MAIN SPIKE CLASS: for types of spikes to inherit from
class BaseSpike:
    def __init__(self,x,y,img,deadly = True):
        self.x = x
        self.y = y
        self.img=img
        self.w= img.width
        self.h = img.height
        self.deadly=deadly
    
    def update(self):
            self.x -= game.scroll_speed
        
    def draw(self):
        image(self.img,self.x,self.y,self.w,self.h)
        
    def collide(self,player):
        return(player.x + player.img_w > self.x and player.x < self.x + self.w and player.y + player.img_h > self.y and player.y < self.y + self.h)

class NormalSpike(BaseSpike):
    def __init__(self,x,y,img):
        BaseSpike.__init__(self,x,y,img)
        self.update_triangle()
        
    def update(self):
        BaseSpike.update(self)
        self.update_triangle()
        
    def update_triangle(self): #for player to collide/interact with an actual triangle and not hitbox from the sprite png
        #triangle vertices
        self.A = (self.x,         self.y + self.h)   # bottom left
        self.B = (self.x + self.w, self.y + self.h)  # bottom right
        self.C = (self.x + self.w/2, self.y)         # top

    #builds triangle
    def point_in_triangle(self, px, py):
        (x1, y1) = self.A
        (x2, y2) = self.B
        (x3, y3) = self.C

        d1 = (px - x2)*(y1 - y2) - (x1 - x2)*(py - y2)
        d2 = (px - x3)*(y2 - y3) - (x2 - x3)*(py - y3)
        d3 = (px - x1)*(y3 - y1) - (x3 - x1)*(py - y1)

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)
    
    def collide(self, player):
        #checks collsions only when spike is near : reduces lag
        if self.x > player.x + player.img_w + 20: 
            return False
        if self.x + self.w < player.x - 20:
            return False
        
        px = player.x
        py = player.y
        w  = player.img_w
        h  = player.img_h

        #check the player's 4 corners
        corners = [(px, py),(px + w, py),(px, py + h),(px + w, py + h)]

        for (cx, cy) in corners:
            if self.point_in_triangle(cx, cy):
                return True

        return False
        
class LeftSpike(BaseSpike):
    def __init__(self,x,y,img):
        BaseSpike.__init__(self,x,y,img)
        
    def draw(self):
        image(self.img,self.x,self.y,self.w,self.h)

#upside down spike  
class UDSpike(BaseSpike):
    def __init__(self,x,single_y,img):
        BaseSpike.__init__(self,x,single_y,img)
        self.y = single_y - self.h
        self.x = x + TILE_W/2 - self.w/2
        
    def draw(self):
        image(self.img,self.x,self.y,self.w,self.h)
        
class SpikeShort(BaseSpike):
    def __init__(self,x,y,img):
        BaseSpike.__init__(self,x,y,img)
        self.h = self.h
        
class MiniSpike(BaseSpike):
    def __init__(self,x,y,img):
        BaseSpike.__init__(self,x,y,img)
        self.h = self.h
    
class Block:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.w = self.img.width
        self.h = self.img.height
        self.deadly = False
    def update(self):
        self.x -= game.scroll_speed
        
    def draw(self):
        image(self.img,self.x,self.y,self.w,self.h)
        
    def collide(self,player):
        return(player.x + player.img_w > self.x and player.x < self.x + self.w and player.y + player.img_h > self.y and player.y < self.y + self.h)
    
class Step:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.w = self.img.width
        self.h = self.img.height
        self.deadly = False
    def update(self):
        self.x -= game.scroll_speed
        
    def draw(self):
        image(self.img,self.x,self.y,self.w,self.h)
        
    def collide(self,player):
        return(player.x + player.img_w > self.x and player.x < self.x + self.w and player.y + player.img_h > self.y and player.y < self.y + self.h)
            

class JumpPad:
    def __init__(self,x,y,img):
        self.x=x
        self.y=y
        self.img=img
        self.w = TILE_W
        self.h = TILE_H
        self.active= True #prevents double boost in same frame
        self.deadly = False
        
    def update(self):
        self.x -= game.scroll_speed
        
    def draw(self):
        image(self.img, self.x,self.y,self.w,self.h)
        
    def boost(self,player):
        player_bottom = player.y + player.img_h
        pad_top = self.y
        pad_left = self.x
        pad_right = self.x + self.w
        
        if (player_bottom<= pad_top and player_bottom + player.vy >= pad_top and player.x + player.img_w > pad_left and player.x < pad_right):
            player.vy = -15 # launches player by -15 pixels upwards to mimic boost effect
            return True
        return False
    
class Chain:
    def __init__(self,x,y,img):
        self.img =img
        self.x = x
        self.y = y
        self.w = img.width
        self.h = img.height
        
        #forces chain to take up 2 tiles vertically
        self.h = TILE_H * 2
        
    def update(self):
        self.x -= game.scroll_speed
        
    def draw(self):
        image(self.img, self.x, self.y, self.w, self.h)
        
class FlightPortal:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.w = img.width
        self.h = img.height
        self.img = img  
        
        #forces image of portal to take up 3 tiles vertically
        self.h = TILE_H * 3
    

    def update(self):
        self.x -= game.scroll_speed

    def draw(self):
        image(self.img, self.x, self.y, self.w, self.h)

# PLAYER CLASS: initialises gravity in runner and flight mode, motion/rotation of square player

class Player:
    def __init__(self, x, y, img, w, h):
        self.x = x
        self.y = y
        self.img = img
        self.img_w = w
        self.img_h = h
        self.mode = "runner"
        self.flight = False
        self.vy = 0
        self.gravity = 0.7
        self.jump_force = -2
        self.on_ground = False
        self.angle = 0
        # current ground y under player
        self.g = SCREEN_H + 100 
        self.prev_y=y 
        
        
    def enter_flight_mode(self):
        self.mode = "flight"
        self.angle = 0
        self.img = IMG_SHIP
        self.img_w = 30
        self.img_h = 20
        
    def update_runner(self):
        self.apply_gravity()
        self.vy += self.gravity
        
        if self.y + self.img_h + self.vy >= self.g:
            # land on platform
            self.y = self.g - self.img_h
            self.vy = 0
            self.on_ground = True
        else:
            # keep falling / moving
            self.y += self.vy
            self.on_ground = False

        # rotation
        if self.on_ground:
            snap = PI / 2
            self.angle = round(self.angle / snap) * snap
        else:
            self.angle += 0.20

    def update_flight(self):
        global keyPressed, key, keyCode
        
        if keyPressed and key == " ":
            self.vy = self.jump_force
        else:
            self.vy += self.gravity
            
        if self.vy > 10:
            self.vy = 10

        # Apply vertical motion
        self.y += self.vy
        if self.y > SCREEN_H - 80:
            APP_STATE = "GAME_OVER"
    
        # tilt the ship at an angle when JUMP is pressed
        self.angle = constrain(self.vy * 0.1, -PI/4, PI/4)
    
    def apply_gravity(self):
        # assume falling until we find a surface under feet
        self.g = SCREEN_H + 10

        player_left   = self.x
        player_right  = self.x + self.img_w
        player_bottom = self.y + self.img_h
        
        #ground collsion
        ground_top = SCREEN_H -90
        if player_bottom + self.vy >= ground_top:
            self.g = ground_top
       
         #platform collisions(blcoks)
        for obj in game.objects:
            if isinstance(obj,BaseSpike): 
                continue
            if not hasattr(obj,"collide"):
                continue    
            
            left = obj.x
            right = obj.x + obj.w
            top = obj.y
            
            if player_right > left and player_left < right: # was above platform, and will cross its top this frame? 
                if player_bottom <= top and player_bottom + self.vy >= top: 
                    self.g = min(self.g, top)

        # checks for horizontal overlap
            if player_right > left and player_left < right:
                # was above platform, and will cross its top this frame?
                if player_bottom <= top and player_bottom + self.vy >= top:
                    self.g = min(self.g, top)

    def update(self):
        self.prev_y = self.y #stores latest position
        if self.mode == "runner":
            self.update_runner()

        elif self.mode == "flight":
            self.update_flight()


    def jump(self):
        if self.on_ground:
            self.vy = -12 #force of jump
            self.on_ground = False

    #draws square sprite + rotation when in air
    def draw_self(self):
        pushMatrix()
        translate(self.x + self.img_w/2, self.y + self.img_h/2)
        rotate(self.angle)
        imageMode(CENTER)
        image(self.img, 0, 0, self.img_w, self.img_h)
        imageMode(CORNER)
        popMatrix()
        

#image rotation helper
def rotate_image(img,angle):
    pg = createGraphics(img.width, img.height)
    pg.beginDraw()
    pg.translate(img.width/2, img.height/2)
    pg.rotate(angle)
    pg.imageMode(CENTER)
    pg.image(img, 0, 0)
    pg.endDraw()
    return pg


# GRID LEVEL MAKER

def load_grid_csv(path):
    """
    Reads a CSV and returns a 2D list of ints.
    Non-numeric cells are ignored.
    """
    grid = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cells = line.split(',')
            row_vals = []
            for cell in cells:
                cell = cell.strip()
                if cell == "":
                    continue
                try:
                    # handles values
                    row_vals.append(int(float(cell)))
                except:
                    # ignores non-numeric like " "
                    pass
            if row_vals:
                grid.append(row_vals)
    return grid

#Level builder helper using cvs values
def build_objects_from_grid(grid):
    """
    Convert grid codes into object instances.
    -1 = empty
     10-99 = platform (width and height can be controlled by first and second digit respectively)
     0 = block
     2 = normal spike
     3 = mini spike
     4 = jump pad
     5 = upside down spike
     6 = short spike
     7 = chain
     8 =step
     9 =Left spike
     1 = portal
    """
    objects = []

    rows = len(grid)
    if rows == 0:
        return objects

    cols = max(len(r) for r in grid)

    # we can set a "ground line" if needed
    global GROUND_Y
    GROUND_Y = SCREEN_H - TILE_H

    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            x = c * TILE_W
            y = r * TILE_H

            if val == -1:
                continue
            #condition to have multi dimesnion platforms using cvs
            if 10<=val <= 99:
                w_mult = val//10
                h_mult = val%10
                objects.append(Platform(x,y,TILE_W * w_mult, TILE_H * h_mult, IMG_PLATFORM))
                continue
            elif val == 0:
                objects.append(Block(x, y, IMG_BLOCK))
            elif val == 2:
                objects.append(NormalSpike(x, y, IMG_SPIKE))
            elif val == 3:
                objects.append(MiniSpike(x, y + (TILE_H-IMG_MINI.height), IMG_MINI))
            elif val ==4:
                objects.append(JumpPad(x,y,IMG_JUMPPAD))
            elif val ==5:
                objects.append(UDSpike(x, y+TILE_H, IMG_UDSPIKE))
            elif val ==6: # align spike so its bottom sits on tile bottom instead of floating
                objects.append(SpikeShort(x, y + (TILE_H - IMG_SHORTSPIKE.height), IMG_SHORTSPIKE))
            elif val ==7:
                objects.append(Chain(x,y,IMG_CHAIN))
            elif val ==8:
                objects.append(Step(x,y,IMG_STEP))
            elif val ==9:
                objects.append(LeftSpike(x,y,IMG_LEFTSPIKE))
            elif val == 1:
                objects.append(FlightPortal(x,y, IMG_PORTAL))

    return objects


#Same object builder helper but for flight mode
def build_objects_from_grid_with_offset(grid, base_row_index, base_y):
    objects = []
    rows = len(grid) 
    if rows == 0: 
        return objects
    
    global GROUND_Y 
    GROUND_Y = SCREEN_H - TILE_H
    
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            x = c * TILE_W
            y = (r-base_row_index) * TILE_H +base_y

            # same object building rules as before:
            if val == -1:
                continue
            if 10 <= val <= 99:
                w_mult = val // 10
                h_mult = val % 10
                objects.append(Platform(x, y, TILE_W*w_mult, TILE_H*h_mult, IMG_PLATFORM))
            elif val == 0:
                objects.append(Block(x, y, IMG_BLOCK))
            elif val == 2:
                objects.append(NormalSpike(x, y, IMG_SPIKE))
            elif val == 3:
                objects.append(MiniSpike(x, y + (TILE_H-IMG_MINI.height), IMG_MINI))
            elif val ==4:
                objects.append(JumpPad(x,y,IMG_JUMPPAD))
            elif val ==5:
                objects.append(UDSpike(x, y+TILE_H, IMG_UDSPIKE))
            elif val ==6:
                objects.append(SpikeShort(x, y + (TILE_H - IMG_SHORTSPIKE.height), IMG_SHORTSPIKE))
            elif val ==7:
                objects.append(Chain(x,y,IMG_CHAIN))
            elif val ==8:
                objects.append(Step(x,y,IMG_STEP))
            elif val ==9:
                objects.append(LeftSpike(x,y,IMG_LEFTSPIKE))
            elif val ==1:
                objects.append(FlightPortal(x,y,IMG_PORTAL))
    return objects


#GAME CLASS: handles all object collisions, flight/runner mode, drawing all objects, level speed

class Game:
    def __init__(self):
        self.state = "runner"
        self.scroll_speed = 5.5
        self.bg_offset = 0
        self.ground = Ground(IMG_GROUND,h=90)
        
        #camera for movement in flight mode
        self.camera_y= 0
        
        #(for progress bar)
        self.distance_traveled = 0
        self.progress = 0

        # player starts at one tile above ground
        self.player = Player(150, SCREEN_H - 2*TILE_H, IMG_PLAYER, 40, 40)

        # Runner csv
        self.grid_path = os.path.join(PATH, "RunnerByLina.csv")
        self.runner_grid = load_grid_csv(self.grid_path)
        self.runner_objects = build_objects_from_grid(self.runner_grid)    

        #Flight csv
        flight_path = os.path.join(PATH, "FlightByRumesa.csv")
        self.flight_grid = load_grid_csv(flight_path)
        # self.flight_objects = build_objects_from_grid(self.flight_grid)
        self.flight_ground_row= 9 #tosit at bottom row
        ground_top= SCREEN_H -90
        
        self.flight_objects = build_objects_from_grid_with_offset(self.flight_grid, self.flight_ground_row, ground_top)
            
        self.objects = self.runner_objects
        self.level_height = (self.flight_ground_row +1) * TILE_H

        
        #computations for progress bar (in pixels)
        runner_cols = len(self.runner_grid[0])
        flight_cols =len(self.flight_grid[0])
        
        #a.convert to pixels
        self.total_pixels = (runner_cols+flight_cols) * TILE_W
        
        #b. subtract screen width for when the last tile scrolls out of view
        self.level_end_x =self.total_pixels - SCREEN_W
    

    def update(self):
        global APP_STATE

        self.bg_offset +=self.scroll_speed * 0.5
        self.distance_traveled += self.scroll_speed #for progress bar
        
        # to gradually increase level speed
        self.scroll_speed += 0.00035
    
        self.player.update()
        
        
        #camera for vertical movement
        if self.state == "flight":
            target_y = self.player.y + self.player.img_h/2 - SCREEN_H/2
            self.camera_y = lerp(self.camera_y, target_y, 0.12) # for camera to move up
            min_cam = -((self.flight_ground_row) * TILE_H)
            max_cam = self.level_height - SCREEN_H
            self.camera_y = constrain(self.camera_y, min_cam, max_cam)
        else:
            self.camera_y =0 #ensures no vertical scroll for runner mode
        
        #reduce lag by printing/updating only what shows on screen
        for obj in self.objects:
                obj.update()
        
        for obj in self.objects:
            if isinstance(obj,JumpPad):
                if obj.boost(self.player):
                    self.player.on_ground = False

        # update objects & check collisions
        for obj in self.objects:
            # obj.update()
            if isinstance(obj,BaseSpike): 
                if obj.collide(self.player):
                    APP_STATE = "GAME_OVER"
                    return
            
        #block/bottom collsions
            if isinstance(obj,Block):
                
                if isinstance(obj, Block):
                    if not obj.collide(self.player):
                        continue  # no collision at all
                
                    # previous and current bottom positions
                    player_prev_bottom = self.player.prev_y + self.player.img_h
                    player_curr_bottom = self.player.y + self.player.img_h
                    block_top = obj.y
                
                    # Landing from above
                    if player_prev_bottom <= block_top and player_curr_bottom >= block_top:
                        # snap to the top of the block
                        self.player.y = block_top - self.player.img_h
                        self.player.vy = 0
                        self.player.on_ground = True
                        continue
                
                    # Side/bottom collisions
                    if self.state == "flight":
                        # In flight mode, sides of blocks wont kill you
                        continue
                
                    # In runner mode, side/bottom hit = death
                    APP_STATE = "GAME_OVER"
                    return
                
            if isinstance(obj,Platform):
                if obj.collide(self.player):
                    
                    player_bottom = self.player.y + self.player.img_h
                    player_top = self.player.y
                    
                    block_top = obj.y
                    block_bottom = obj.y + obj.h
                    
                    #allowed landing
                    if abs(player_bottom - block_top)<2:
                        continue
                
                #otherwise side collisons=death
                    APP_STATE = "GAME_OVER"
    
                    return
            
            if isinstance(obj, Step):
                if obj.collide(self.player):
                    
                    player_bottom = self.player.y + self.player.img_h
                    next_bottom = player_bottom + self.player.vy
    
                    block_top = obj.y
    
                    # landing: player was above and is falling onto it
                    if player_bottom <= block_top and next_bottom >= block_top:
                        # correct the landing
                        self.player.y = block_top - self.player.img_h
                        self.player.vy = 0
                        self.player.on_ground = True
                        continue
                    
        
            if isinstance(obj, FlightPortal):
                # Player is in RUNNER mode --> portal 1 --> enter flight
                if self.state == "runner" and abs(obj.x - self.player.x) < 30:
                    self.state = "flight"
                    self.player.enter_flight_mode()
                    self.objects = self.flight_objects
                    self.player.y = SCREEN_H/2
                    return
            
                # Player is in FLIGHT --> portal 2 --> level complete!
                if self.state == "flight" and abs(obj.x - self.player.x) < 30:
                    APP_STATE = "LEVEL_COMPLETE"
                    return
  
        self.ground.update()
        # self.player.update()
        
        #Percent progress
        self.progress = constrain((self.distance_traveled/ float(self.level_end_x))*100,0,100)

    def draw(self):
        # background
        background(20)
        
        pushMatrix() # push -pop whole draw() function to implement camera
        translate(0,-self.camera_y)
    
        scroll_x = self.bg_offset % IMG_BG.width
        scroll_x = self.bg_offset % IMG_BG.width
        bg_h = IMG_BG.height
        
        tiles_vertical = int((self.level_height + SCREEN_H * 3) // bg_h) + 5
        
        start_y = -SCREEN_H * 2
        for i in range(3):
            y_pos = start_y + i * bg_h
            image(IMG_BG, -scroll_x, y_pos)
            image(IMG_BG, -scroll_x + IMG_BG.width, y_pos)
        
            
        self.ground.draw()
        
        #to reduce lag
        for obj in self.objects:
            if VISIBLE_LEFT < obj.x < VISIBLE_RIGHT:
                obj.draw()
        
        self.player.draw_self()
        
        popMatrix()
        
        # UI
        fill(255)
        textSize(14)
        textAlign(LEFT, TOP)
        text("SPACE: jump", 10, 10)
        
        #Progress Bar:
        bar_x = 150
        bar_y = 15
        bar_w = SCREEN_W - 500
        bar_h = 8
        
        #a. outline of progress bar
        noFill()
        stroke(255)
        strokeWeight(3)
        rect(bar_x,bar_y, bar_w,bar_h,10)
        
        #b. filled amount
        noStroke()
        fill(0,180,255)
        fill_w = bar_w * (self.progress / 100.0)
        rect(bar_x, bar_y,fill_w,bar_h,10)
        
        #c. % text
        fill(255)
        textSize(20)
        textAlign(LEFT,TOP)
        text(str(int(self.progress))+ "%", bar_x,bar_y + 20)
        
            
# UI
def intro_screen():
    background(0)
    image(menu_img, 0, 0, SCREEN_W, SCREEN_H)

    draw_button(play_btn, "PLAY")
    draw_button(how_btn, "INSTRUCTIONS")
    draw_button(skin_btn, "CHOOSE SKIN")


def draw_button(btn, label):
    if btn["x"] < mouseX < btn["x"] + btn["w"] and btn["y"] < mouseY < btn["y"] + btn["h"]:
        fill(100, 200, 255)
    else:
        fill(0, 150, 255)
    
    rect(btn["x"], btn["y"], btn["w"], btn["h"], 10)
    #white borders
    noFill()
    stroke(255)
    strokeWeight(4)
    rect(btn["x"], btn["y"], btn["w"], btn["h"], 10)
    noStroke()
    
    fill(255)
    textFont(myFont)
    textSize(28)
    textAlign(CENTER, CENTER)
    text(label, btn["x"] + btn["w"]/2, btn["y"] + btn["h"]/2)

def show_instructions():
    # fullscreen tutorial image
    imageMode(CORNER)
    image(IMG_TUTORIAL, 0, 0, SCREEN_W, SCREEN_H)

    # title
    fill(255)
    textFont(myFont)
    textAlign(LEFT, TOP)
    textSize(35)
    text("HOW TO PLAY:", 30, 20)

    # instructions on left side
    textSize(26)
    txt_y = 120
    text("Press SPACE to jump\n\n\n"
         "Jump to spikes and \nobstacles\n\n\n"
         "Jump on orb to \nboost-jump", 30, txt_y)

    # return message
    textAlign(CENTER, CENTER)
    textSize(20)
    fill(255)
    text("Click anywhere to return", 200, SCREEN_H - 30)
    
def show_skin_menu():
    global CHOSEN_SKIN
    
    background(20)

    textFont(myFont)
    fill(255)
    textAlign(CENTER, TOP)
    textSize(40)
    text("CHOOSE YOUR SKIN", SCREEN_W/2, 20)

    # load preview images for user to choose from
    img1 = loadImage(PATH + "/images/player.png")
    img2 = loadImage(PATH + "/images/player2.png")
    img3 = loadImage(PATH + "/images/player3.png")
    img4 = loadImage(PATH + "/images/player4.png")
    img5 = loadImage(PATH + "/images/player5.png")
    

    image(img1, 60, 150, 80, 80)
    image(img2, 210, 150, 80, 80)
    image(img3, 360, 150, 80, 80)
    image(img4, 510, 150, 80, 80)
    image(img5, 660, 150, 80, 80)

    textSize(20)
    text("Click to select skin", SCREEN_W/2, SCREEN_H - 40)
    
def show_game_over():
    
    fill(255)
    textFont(myFont)
    textAlign(CENTER, TOP)
    textSize(60)
    text("GAME OVER", SCREEN_W/2, 80)

    #shows final progress
    textSize(30)
    text("Progress: " + str(int(game.progress)) + "%", SCREEN_W/2, 160)

    # buttons
    draw_button(restart_btn, "RESTART")
    draw_button(menu_btn, "MAIN MENU")
    
def show_complete():
    fill(255)
    textFont(myFont)
    textAlign(CENTER, CENTER)
    textSize(60)
    text("LEVEL COMPLETE!" , SCREEN_W/2, SCREEN_H/2-40)
    draw_button(menu_btn, "MAIN MENU")
    


# Processing Hooks

def setup():
    global game
    global IMG_PLAYER, IMG_BLOCK, IMG_SPIKE, IMG_MINI, IMG_BG, IMG_GROUND, IMG_JUMPPAD, IMG_PLATFORM, IMG_SHORTSPIKE, IMG_CHAIN, IMG_UDSPIKE, IMG_STEP, IMG_LEFTSPIKE, IMG_SHIP, IMG_PORTAL
    global menu_img,play_btn, how_btn, IMG_TUTORIAL, skin_btn, CHOSEN_SKIN, restart_btn, menu_btn, LEVEL_COMPLETE
    global myFont, minim, music

    myFont=createFont("PUSAB.otf",48)
    textFont(myFont)

    size(SCREEN_W, SCREEN_H)
    frameRate(60)
    
    button_w = 350
    button_h = 60
    center_x = (SCREEN_W - button_w) / 2
    
    play_btn = {"x": center_x, "y": 200, "w": button_w, "h": button_h}
    how_btn  = {"x": center_x, "y": 280, "w": button_w, "h": button_h}
    skin_btn = {"x": center_x, "y": 360, "w": button_w, "h": button_h}
    
    #game over menu
    restart_btn = {"x": SCREEN_W/2 - 175, "y": 250, "w": 350, "h": 60}
    menu_btn    = {"x": SCREEN_W/2 - 175, "y": 330, "w": 350, "h": 60}

    IMG_PLAYER = loadImage(PATH + "/images/" + CHOSEN_SKIN)
    IMG_BLOCK  = loadImage(PATH + "/images/block.png")   
    IMG_SPIKE  = loadImage(PATH + "/images/spike.png")
    IMG_MINI   = loadImage(PATH + "/images/mini_spike.png")
    IMG_BG     = loadImage(PATH + "/images/layer.png")  
    IMG_GROUND= loadImage(PATH + "/images/ground.png")
    IMG_JUMPPAD = loadImage(PATH + "/images/jump_pad.png")
    IMG_PLATFORM= loadImage(PATH + "/images/platform.png")
    IMG_SHORTSPIKE = loadImage (PATH + "/images/shortspike.png")
    IMG_CHAIN = loadImage (PATH + "/images/chain.png")
    IMG_UDSPIKE = loadImage(PATH + "/images/UDspike.png")
    IMG_STEP = loadImage(PATH + "/images/step.png")
    IMG_LEFTSPIKE = rotate_image(IMG_SPIKE, -PI/2)
    menu_img = loadImage(PATH + "/images/background.png")
    IMG_TUTORIAL = loadImage(PATH + "/images/tutorial.png")
    IMG_PORTAL = loadImage(PATH + "/images/portal.png")
    IMG_SHIP = loadImage(PATH + "/images/ship.png")
    

    IMG_BLOCK.resize(TILE_W, TILE_H)
    IMG_SPIKE.resize(TILE_W, TILE_H)
    # IMG_MINI.resize(200, 40)
    IMG_GROUND.resize(SCREEN_W,80)
    IMG_TUTORIAL.resize(SCREEN_H, SCREEN_W)
    
    #Music to play throughout game
    # minim = Minim(this)
    # music = minim.loadFile("music.mp3")
    # music.loop()

    game = Game()


def draw():
    # print(frameRate)
    global APP_STATE, game
    if APP_STATE == "MENU":
        intro_screen()
        return
    if APP_STATE == "INSTRUCTIONS":
        show_instructions()
        return
    if APP_STATE == "SKIN_MENU":
        show_skin_menu()
        return
    if APP_STATE == "GAME":
        game.update()
        game.draw()
        return
    if APP_STATE == "GAME_OVER":
        game.draw()
        show_game_over()
        return
    if APP_STATE == "LEVEL_COMPLETE":
        show_complete()
        return


def keyPressed():
    if APP_STATE == "GAME" and game.state == "runner":
        if key == ' ':
            game.player.jump()
        
def mousePressed():
    global APP_STATE, game, CHOSEN_SKIN, IMG_PLAYER

    if APP_STATE == "MENU":
        if play_btn["x"] < mouseX < play_btn["x"] + play_btn["w"] and \
           play_btn["y"] < mouseY < play_btn["y"] + play_btn["h"]:
        
            IMG_PLAYER = loadImage(PATH + "/images/" + CHOSEN_SKIN)

            # Start a NEW game instance when PLAY is pressed
            game = Game()
            APP_STATE = "GAME"
            return

        if how_btn["x"] < mouseX < how_btn["x"] + how_btn["w"] and \
       how_btn["y"] < mouseY < how_btn["y"] + how_btn["h"]:
            APP_STATE = "INSTRUCTIONS"
        
            return
        if skin_btn["x"] < mouseX < skin_btn["x"] + skin_btn["w"] and \
       skin_btn["y"] < mouseY < skin_btn["y"] + skin_btn["h"]:
            APP_STATE = "SKIN_MENU"
        
            return

    elif APP_STATE == "INSTRUCTIONS":
        # Clicking anywhere returns
        APP_STATE = "MENU"
        
    elif APP_STATE == "SKIN_MENU":
        if 60 < mouseX < 140 and 150 < mouseY < 230:
            CHOSEN_SKIN = "player.png"
            APP_STATE = "MENU"
            return
        if 210 < mouseX < 290 and 150 < mouseY < 230:
            CHOSEN_SKIN = "player2.png"
            APP_STATE = "MENU"
            return
        if 360 < mouseX < 440 and 150 < mouseY < 230:
            CHOSEN_SKIN = "player3.png"
            APP_STATE = "MENU"
            return
        if 510 < mouseX < 590 and 150 < mouseY < 230:
            CHOSEN_SKIN = "player4.png"
            APP_STATE = "MENU"
            return
        if 660 < mouseX < 740 and 150 < mouseY < 230:
            CHOSEN_SKIN = "player5.png"
            APP_STATE = "MENU"
            return
        
    elif APP_STATE == "GAME_OVER":
            # Restart
        if restart_btn["x"] < mouseX < restart_btn["x"] + restart_btn["w"] and \
        restart_btn["y"] < mouseY < restart_btn["y"] + restart_btn["h"]:
            game = Game()
            APP_STATE = "GAME"
            # music.rewind()
            # music.play()
            
            return
    
        # Main menu
        if menu_btn["x"] < mouseX < menu_btn["x"] + menu_btn["w"] and \
        menu_btn["y"] < mouseY < menu_btn["y"] + menu_btn["h"]:
            APP_STATE = "MENU"
            # music.pause()
            return
        
        
