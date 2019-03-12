import tkinter as tk
from tkinter import messagebox
import random
from random import randint
import time
import copy
import os
import pygame as pg
import sys
from rotate_array import rotate_array as ra
c = []
for filename in os.listdir(r"C:\Users\owner\Desktop\tetris"):
                if filename.endswith(".wav") and filename != "line.wav" and filename != "clear.wav":
                    c.append(filename)
x = randint(0, (len(c))-1)
class Shape:
    def __init__(self, shape, key, piece, row, column, coords):
        self.shape = shape
        self.piece = piece
        self._row = row
        self.key = key
        self.column = column
        self.coords = coords
        self.hover_time = self.spin_time = time.perf_counter()
        self._rotation_index = 0

    @property
    def row(self):
        return self._row
    @row.setter
    def row(self, x):
        if x != self._row:
            self._row = x
            self.hover_time = time.perf_counter()
    @property
    def rotation_index(self):
        return self._rotation_index
    @rotation_index.setter
    def rotation_index(self, x):
        self._rotation_index = x
        self.spin_time = time.perf_counter()
    @property
    def hover(self):
        return time.perf_counter() - self.hover_time < 0.5
    @property
    def spin(self):
        return time.perf_counter() - self.spin_time < 0.5

class Tetris:
    def __init__(self, parent, event=None):
        self.parent = parent
        parent.title('Tetris')
        self.spin = 'nospin' not in sys.argv[1:]
        self.hover = 'nohover' not in sys.argv[1:]
        self.random = 'random' in sys.argv[1:]
        
        self.music()
            
        self.board_width = 10
        self.board_height = 24
        self.high_score = 0
        self.high_score_lines = 0
        self.width = 200
        self.height = 480
        self.square_width = self.width//10
        self.max_speed_score = 1000
        self.speed_factor = 35
        
        
        self.shapes = { 's':[['*', ''],
                            ['*', '*'],
                            ['', '*']],
                        'z':[['', '*'],
                            ['*', '*'],
                            ['*', '']],
                        'r':[['*', '*'],
                            ['*', ''],
                            ['*', '']],
                        'L':[['*', ''],
                            ['*', ''],
                            ['*', '*']],
                        'o':[['*', '*'],
                            ['*', '*']],
                        'I':[['*'],
                            ['*'],
                            ['*'],
                            ['*']],
                        'T':[['*', '*', '*'],
                            ['', '*', '']],
                        'j':[['', '*', '*'],
                             ['', '*', ''],
                             ['', '*', ''],
                             ['*', '*', '']]
                      }

        self.colors = {'s':'green',
                        'z':'goldenrod',
                        'r':'turquoise',
                        'L':'red',
                        'o':'slateblue',
                        'I':'slategray',
                        'T':'violet'}
        for key in ('<Down>', '<Left>', '<Right>',
                     'a', 'A', 's', 'S', 'd', 'D'):
            self.parent.bind(key, self.shift)
        for key in ('<Up>', 'w', 'W', 'q', 'Q', 'e', 'E'):
            self.parent.bind(key, self.rotate)
        for key in ('<space>', '<Shift_R>', '<Prior>', '<Next>'):
            self.parent.bind(key, self.snap)
        self.parent.bind('<Escape>', self.pause)
        self.parent.bind('p', self.draw_board)
        self.parent.bind('P', self.draw_board)
        self.parent.bind('m', self.toggle_audio)
        self.parent.bind('c', self.toggle_audio)
        self.parent.bind('t', self.toggle_audio)
        self.parent.bind('g', self.toggle_guides)
        self.parent.bind('G', self.toggle_guides)
        self.canvas = None
        self.preview_canvas = None
        self.ticking = None
        self.spawning = None
        self.guide_fill = 'black'
        self.score_var = tk.StringVar()
        self.high_score_var = tk.StringVar()
        self.high_score_var.set('Highscore:\n0 (0)')
        self.preview_label = tk.Label(root, text='Next piece:',
                                     width=15,
                                     font=('Arial Black', 12))
        self.preview_label.grid(row=0, column=1, sticky='S')
        self.score_label = tk.Label(root, textvariable=self.score_var,
                                     width=15, height=5,
                                     font=('Arial Black', 12))
        self.score_label.grid(row=2, column=1, sticky='S')
        self.high_score_label = tk.Label(root,
                                         textvariable=self.high_score_var,
                                         width=15,
                                         height=5,
                                         font=('Arial Black', 12))
        self.high_score_label.grid(row=3, column=1, sticky='N')
        def helloCallBack():
            msgbox = messagebox.askquestion( "Tetris Controls", "PRESS 'YES' OR ENTER TO PAUSE GAME")
            if msgbox == "yes":
                self.pause()
                messagebox.showinfo("Tetris Controls", "Letters are not case sensitive:\n\nMove piece - ASD/Arrow keys\nRotate piece - QWE/Arrow up\nSnap piece - Space/Right shift\n---------------\nPause game - ESC\nNew game - P\n---------------\nPause song - M\nContinue song - C\nNext song - T\n---------------\nToggle guidelines - G")
                self.pause()

        B = tk.Button(root, text ="Controls", width=6, height=1, font=('Arial Black', 12), command = helloCallBack, activeforeground='Blue')

        B.grid(row=4, column=1)
        
        self.draw_board()

    
       
    def draw_board(self, event=None):
        if self.ticking:
            self.parent.after_cancel(self.ticking)
        if self.spawning:
            self.parent.after_cancel(self.spawning)
        self.score_var.set('Score:\n0')
        self.board = [['' for column in range(self.board_width)]
                        for row in range(self.board_height)]
        self.field = [[None for column in range(self.board_width)]
                        for row in range(self.board_height)]
        if self.canvas:
            self.canvas.destroy()
        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0, rowspan=5)
        self.h_separator = self.canvas.create_line(0,
                                                   self.height//6,
                                                   self.width,
                                                   self.height//6, 
                                                  width=2)
        self.v_seperator = self.canvas.create_line(self.width,
                                                    0,
                                                    self.width,
                                                    self.height,
                                                    width=2)
        if self.preview_canvas:
            self.preview_canvas.destroy()
        self.preview_canvas = tk.Canvas(root,
                                        width=5*self.square_width,
                                        height=5*self.square_width)
        self.preview_canvas.grid(row=1, column=1)
        
        self.tickrate = 1000
        self.score = 0
        self.score_lines = 0
        self.piece_is_active = False
        self.paused = False
        self.bag = []
        self.preview()
        
        self.guides = [self.canvas.create_line(0, 0, 0, self.height),
                       self.canvas.create_line(
                            self.width,
                            0,
                            self.width,
                            self.height
                        )]
                        
        self.spawning = self.parent.after(self.tickrate, self.spawn)
        self.ticking = self.parent.after(self.tickrate, self.tick)

    def toggle_guides(self, event=None):
        self.guide_fill = '' if self.guide_fill else 'black'
        self.canvas.itemconfig(self.guides[0], fill=self.guide_fill)
        self.canvas.itemconfig(self.guides[1], fill=self.guide_fill)

    def music(self):
        pg.mixer.init(buffer=512)
        pg.mixer.music.load(c[x])
        pg.mixer.music.stop()
        pg.mixer.Channel(0).play(pg.mixer.Sound(c[x]))
        self.queue()

    def queue(self):
        global x, c
        pos = pg.mixer.Channel(0).get_busy()
        if pos == False:
            x -= 1
            pg.mixer.music.load(c[x])
            pg.mixer.Channel(0).play(pg.mixer.Sound(c[x]))

        root.after(1, self.queue)
        
   
    def toggle_audio(self, event=None):        
        self.isPaused = False
        songpause = (event and event.keysym)
        songunpause = (event and event.keysym)
        other_song = (event and event.keysym)
        position = pg.mixer.music.get_pos()
        if songpause == 'm' and self.isPaused == False:
            pg.mixer.Channel(0).pause()
            self.isPaused = True
        elif songunpause == 'c':
            pg.mixer.Channel(0).unpause()
            self.isPaused = False
        elif other_song == 't':
            global x
            x = randint(0, (len(c))-1)
            pg.mixer.init(buffer=512)
            pg.mixer.music.load(c[x])
            pg.mixer.Channel(0).stop()
            pg.mixer.Channel(0).play(pg.mixer.Sound(c[x]))
               

    def pause(self, event=None):
        if self.piece_is_active and not self.paused:
            self.paused = True
            pg.mixer.Channel(0).pause()
            self.isPaused = True
            self.piece_is_active = False
            self.parent.after_cancel(self.ticking)
        elif self.paused:
            self.paused = False
            pg.mixer.Channel(0).unpause()
            self.isPaused = False
            self.piece_is_active = True
            self.ticking = self.parent.after(self.tickrate, self.tick)
    def tick(self):
        if self.piece_is_active and not self.spin or not self.active_piece.spin:
            self.shift()
        self.ticking = self.parent.after(self.tickrate, self.tick)
    
    def check(self,shape, r, c, l , w):
        for row, squares in zip(range(r, r+l), shape):
            for column, square in zip(range(c, c+w), squares):
                if (row not in range(self.board_height)
                    or
                    column not in range(self.board_width)
                    or
                    (square and self.board[row][column] == 'x')
                    ): #also, make sure it's on the board
                    # print(row, column, square, self.board[row][column])
                    return
        return True
    
    def move(self, shape, r, c, l, w):
        square_idxs = iter(range(4)) # iterator of 4 indices
        # Remove shape from board
        for row in self.board:
            row[:] = ['' if cell == '*' else cell for cell in row]
        
        # Put shape onto board and piece onto canvas
        for row, squares in zip(range(r, r+l),shape):                              
            for column, square in zip(range(c, c+w), squares):
                if square:
                    self.board[row][column] = square
                    square_idx = next(square_idxs)
                    coord = (column*self.square_width,
                            row*self.square_width,
                            (column+1)*self.square_width,
                            (row+1)*self.square_width)
                    self.active_piece.coords[square_idx] = coord
                    self.canvas.coords(self.active_piece.piece[square_idx],
                                        coord)
        self.active_piece.row = r
        self.active_piece.column = c
        self.active_piece.shape = shape
        self.move_guides(c, c+w)
        return True

    def check_and_move(self, shape, r, c, l, w):
        
        return self.check(shape, r, c, l, w
            ) and self.move(shape, r, c, l, w)
        

    def rotate(self, event=None):
        if not self.piece_is_active:
            return
        if len(self.active_piece.shape) == len(self.active_piece.shape[0]):
            self.active_piece.rotation_index = self.active_piece.rotation_index
            return
        r = self.active_piece.row
        c = self.active_piece.column
        l = len(self.active_piece.shape)
        w = len(self.active_piece.shape[0]) 
        x = c + w//2 # center column for old shape
        y = r + l//2 # center row for old shape
        direction = event.keysym
        if direction in {'q', 'Q'}:
            shape = ra(self.active_piece.shape, -90)
            rotation_index = (self.active_piece.rotation_index - 1) % 4 
            # 4 is a magic number, number of sides of a rectangle
            rx,ry = self.active_piece.rotation[rotation_index]
            rotation_offsets = -rx,-ry
        elif direction in {'e', 'E', '0', 'Up', 'w', 'W'}:
            shape = ra(self.active_piece.shape, 90)
            rotation_index = self.active_piece.rotation_index
            rotation_offsets = self.active_piece.rotation[rotation_index]
            rotation_index = (rotation_index + 1) % 4

        l = len(shape) # length of new shape
        w = len(shape[0]) # width of new shape
        rt = y - l//2 # row of new shape
        ct = x - w//2 # column of new shape

        x_correction, y_correction = rotation_offsets
        rt += y_correction
        ct += x_correction

        # rotation prefers upper left corner -
        # possibly hard-code a specific center square
        # for each piece/shape          
        if not self.check_and_move(shape, rt, ct, l, w):
            return

        self.active_piece.rotation_index = rotation_index          
        
    def shift(self, event=None):
        down = {'Down', 's', 'S'}
        left = {'Left', 'a', 'A'}
        right = {'Right', 'd', 'D'}
        if not self.piece_is_active:
            return
        r = self.active_piece.row
        c = self.active_piece.column
        l = len(self.active_piece.shape)
        w = len(self.active_piece.shape[0])
        direction = (event and event.keysym) or 'Down'
        if direction in down:
            rt = r+1 # row, temporary
            ct = c # column, temporary
        elif direction in left:
            rt = r
            ct = c-1
        elif direction in right:
            rt = r
            ct = c+1

        success = self.check_and_move(self.active_piece.shape, rt, ct, l, w)
        
        if direction in down and not success and not (self.hover and self.active_piece.hover):
            self.settle()
        
    def settle(self):
        self.piece_is_active = False
        for row in self.board:
            row[:] = ['x' if cell == '*' else cell for cell in row]
        for (x1, y1, x2, y2),ide in zip(self.active_piece.coords, self.active_piece.piece):
            self.field[y1//self.square_width][x1//self.square_width] = ide
        indices = [idx for idx,row in enumerate(self.board) if all(row)]
        if indices: # clear rows, score logic, etc
            self.score += (1, 2, 5, 10)[len(indices)-1]
            self.score_lines += len(indices)
            self.clear(indices)
            if all(not cell for row in self.board for cell in row):
                self.score += 10
            self.high_score = max(self.score, self.high_score)
            self.high_score_lines = max(self.score_lines, self.high_score_lines)
            self.score_var.set('Score:\n{} ({})'.format(self.score, self.score_lines))
            self.high_score_var.set('Highscore:\n{} ({})'.format(self.high_score, self.high_score_lines))
            if self.score <= self.max_speed_score:
                self.tickrate = 1000 // (self.score//self.speed_factor + 1)
                
        if any(any(row) for row in self.board[:4]):
            self.lose()
            return
        self.spawning = self.parent.after(500 if indices and self.tickrate<500 else self.tickrate, self.spawn)
        
    def preview(self):
        self.preview_canvas.delete(tk.ALL)
        if not self.bag:
            if self.random:
                self.bag.append(random.choice('szoLrTI'))
            else:
                self.bag = random.sample('szoLrTI', 7)
        key = self.bag.pop()
        shape = ra(self.shapes[key], random.choice((0, 90, 180, 270)))
        self.preview_piece = Shape(shape, key, [], 0, 0, [])
        width = len(shape[0])
        half = self.square_width//2
        for y,row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.preview_piece.coords.append((self.square_width*x+half,
                                                     self.square_width*y+half,
                                                     self.square_width*(x+1)+half,
                                                     self.square_width*(y+1)+half))
                    self.preview_piece.piece.append(
                    self.preview_canvas.create_rectangle(self.preview_piece.coords[-1],
                                                 fill = self.colors[key],
                                                 width = 3))

        self.preview_piece.rotation_index = 0
        self.preview_piece.i_nudge = (len(shape) < len(shape[0])
                                    ) and 4 in (len(shape), len(shape[0]))
        self.preview_piece.row = self.preview_piece.i_nudge
        if 3 in (len(shape), len(shape[0])):
            self.preview_piece.rotation = [(0,0),
                                          (1,0),
                                          (-1,1),
                                          (0,-1)]
        else:
            self.preview_piece.rotation = [(1,-1),
                                            (0,1),
                                            (0,0),
                                            (-1,0)]
        if len(shape) < len(shape[0]): # wide shape
            self.preview_piece.rotation_index += 1

    def move_guides(self, left, right):
        left *= self.square_width
        right *= self.square_width
        self.canvas.coords(self.guides[0], left, 0, 
                                    left,
                                    self.height)
        self.canvas.coords(self.guides[1], right, 0,
                                right,
                                self.height)

    def spawn(self):
        self.piece_is_active = True
        self.active_piece = copy.deepcopy(self.preview_piece)
        self.preview()
        width = len(self.active_piece.shape[0])
        start = (10-width)//2
        self.active_piece.column = start
        self.active_piece.start = start
        self.active_piece.coords = []
        self.active_piece.piece = []
        for y,row in enumerate(self.active_piece.shape):
            self.board[y+self.active_piece.i_nudge][start:start+width] = self.active_piece.shape[y]
            for x, cell in enumerate(row, start=start):
                if cell:
                    self.active_piece.coords.append((self.square_width*x,
                                                     self.square_width*(y+self.active_piece.i_nudge),
                                                     self.square_width*(x+1),
                                                     self.square_width*(y+self.active_piece.i_nudge+1)))
                    self.active_piece.piece.append(
                    self.canvas.create_rectangle(self.active_piece.coords[-1],
                                                 fill = self.colors[self.active_piece.key],
                                                 width = 3))
        self.move_guides(start, start+width)

    def lose(self):
        self.piece_is_active = False
        self.parent.after_cancel(self.ticking)
        self.parent.after_cancel(self.spawning)
        self.clear_iter(range(len(self.board)))
        

    def snap(self, event=None):
        down = {'space', 'Shift_R'}
        left = {'Prior'}
        right = {'Next'}
        if not self.piece_is_active:
            return
        r = self.active_piece.row
        c = self.active_piece.column
        l = len(self.active_piece.shape)
        w = len(self.active_piece.shape[0])
        
        direction = event.keysym
        if direction in down:
            rt = r+1 # row, temporary
            ct = c # column, temporary
        elif direction in left:
            rt = r
            ct = c-1
        elif direction in right:
            rt = r
            ct = c+1
        while 1:
            if self.check(self.active_piece.shape,
                              r+(direction in down),
                              c+(direction in right)-(direction in left),
                              l, w):
                r += direction in down
                c += (direction in right) - (direction in left)
            else:
                break

        self.move(self.active_piece.shape, r, c, l, w)
        
        if direction in down:
            self.settle()
        

    def clear(self, indices):
        for idx in indices:
            pg.mixer.music.load('line.wav')
            pg.mixer.Channel(1).play(pg.mixer.Sound('line.wav'))
            self.board.pop(idx)
            self.board.insert(0, ['' for column in range(self.board_width)])
        self.clear_iter(indices)

    def clear_iter(self, indices, current_column=0):
        for row in indices:
            if row%2:
                cc = current_column
            else:
                cc = self.board_width - current_column-1
            ide = self.field[row][cc]
            self.field[row][cc] = None
            self.canvas.delete(ide)
        if current_column < self.board_width-1:
            self.parent.after(50, self.clear_iter, indices, current_column+1)
        else:
            for idx,row in enumerate(self.field):
                offset = sum(r > idx for r in indices)*self.square_width
                for square in row:
                    if square:
                        self.canvas.move(square, 0, offset)
            for row in indices:
                self.field.pop(row)
                self.field.insert(0, [None for x in range(self.board_width)])
            


root = tk.Tk()
tetris = Tetris(root)
root.mainloop()





