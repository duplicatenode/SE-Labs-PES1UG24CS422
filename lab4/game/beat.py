import pygame
import random

LANES = 4
LANE_KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
LANE_LABELS = ['D', 'F', 'J', 'K']
LANE_COLORS = [(220,80,80),(80,180,220),(100,220,100),(220,180,60)]

# Note kinds
NORMAL = "normal"
HOLD = "hold"
HOLD_SECONDS = 1.0  # how long a hold note must be held (converted to frames by the engine)

class Note:
    WIDTH = 70
    HEIGHT = 20
    def __init__(self, lane, y=-30, speed=4, kind=NORMAL, hold_frames=0):
        self.lane = lane
        self.y = y              # top of the note "head" (the part that must reach the hit line)
        self.speed = speed
        self.hit = False        # normal note: hit. hold note: fully completed (also set on completion)
        self.missed = False     # normal note: passed the line. hold note: never started OR released early
        # --- hold-note state (unused by normal notes) ---
        self.kind = kind
        self.hold_frames = hold_frames if kind == HOLD else 0  # frames the key must stay down
        self.held_frames = 0    # frames held so far
        self.holding = False    # player has started holding it and is still holding
        self.completed = False  # hold finished successfully (scored exactly once)
        self.grade = None       # timing grade of the initial press (PERFECT/GREAT/OK)
        self.points = 0
        self.color = None

    @property
    def is_hold(self):
        return self.kind == HOLD

    @property
    def tail_length(self):
        # Full tail length in pixels: the distance the note travels during the hold time.
        return self.speed * self.hold_frames if self.is_hold else 0

    @property
    def tail_remaining(self):
        # Tail shrinks as the hold progresses.
        if not self.is_hold or self.hold_frames == 0:
            return 0
        return self.tail_length * (1 - min(1.0, self.held_frames / self.hold_frames))

    def update(self):
        if self.holding:   # a note being held stays pinned on the hit line
            return
        self.y += self.speed

    def get_rect(self, lane_x):
        return pygame.Rect(lane_x - self.WIDTH//2, int(self.y), self.WIDTH, self.HEIGHT)
        #got the beats to work
