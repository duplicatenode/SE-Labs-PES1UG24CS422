import os
from collections import deque
import pygame
import random
from game.beat import Note, LANES, LANE_KEYS, LANE_LABELS, LANE_COLORS, NORMAL, HOLD, HOLD_SECONDS

WIDTH, HEIGHT = 480, 640
FPS = 60
HIT_Y = HEIGHT - 80
HIT_WINDOW = 30
HOLD_FRAMES = round(HOLD_SECONDS * FPS)  # 1 second at 60 FPS = 60 frames
# --- BPM-synced spawning (Task 3) ---
BPM = 120                           # beats per minute (fixed; never changed during play)
BEAT_INTERVAL_MS = 60000 / BPM      # 120 BPM -> 2 beats/sec -> 500.0 ms per beat
FRAME_MS = 1000 / FPS               # nominal frame length (16.67 ms), used when no dt is supplied
MAX_DT_MS = 100                     # clamp one frame's dt (e.g. after dragging the window) so we never flood-spawn
SPEEDUP_EVERY_MS = 10000            # difficulty ramp every 10 s (was frame % 600 == 0 at 60 FPS)
# Set RHYTHM_DEBUG_BPM=1 in the environment to print every beat's scheduled vs. actual spawn time.
DEBUG_BPM = os.environ.get("RHYTHM_DEBUG_BPM") == "1"
HOLD_CHANCE = 0.25                      # ~25% of notes are hold notes
BG = (15, 10, 25)
LANE_W = WIDTH // LANES
HIT_SOUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "hit.wav")

class GameEngine:
    def __init__(self):
        pygame.init()
        self.hit_sound = self._load_hit_sound()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Rhythm Tap")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 26, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 44, bold=True)
        self.reset()

    def _load_hit_sound(self):
        # Audio is optional: any failure (no device, missing/corrupt file) just means no sound.
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sound = pygame.mixer.Sound(HIT_SOUND_PATH)
            sound.set_volume(0.4)
            return sound
        except (pygame.error, FileNotFoundError, OSError):
            return None

    def _play_hit_sound(self):
        if self.hit_sound is None:
            return
        try:
            self.hit_sound.play()
        except pygame.error:
            pass

    def _count_grade(self, grade):
        if grade == "PERFECT":
            self.perfect_count += 1
        elif grade == "GREAT":
            self.great_count += 1
        elif grade == "OK":
            self.ok_count += 1

    def _register_miss(self):
        # The ONE place a missed note is recorded (used by both auto-miss and failed hold).
        self.misses += 1
        self.miss_count += 1
        self.combo = 0

    def accuracy(self):
        hits = self.perfect_count + self.great_count + self.ok_count
        judged = hits + self.miss_count
        return (hits / judged * 100) if judged else 0.0

    def reset(self):
        self.notes = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.misses = 0
        # Grade breakdown for the game-over summary. miss_count counts judged NOTES that were missed
        # (passed the hit window, or a hold released early) - same events as self.misses, tracked separately.
        self.perfect_count = 0
        self.great_count = 0
        self.ok_count = 0
        self.miss_count = 0
        self.speed = 5
        self.frame = 0
        # BPM clock: game time in ms (sum of frame dt's) and the index of the next beat to spawn.
        # Beat n is scheduled at exactly n * BEAT_INTERVAL_MS, so errors never accumulate.
        self.elapsed_ms = 0.0
        self.next_beat = 0
        self.next_speedup_ms = SPEEDUP_EVERY_MS
        self.beat_log = deque(maxlen=256)  # (beat_index, scheduled_ms, actual_ms, spawned) for verification
        self.feedback = []  # (text, color, ttl, x, y)
        self.game_over = False

    def _lane_blocked(self, lane):
        # Don't spawn a note into a lane whose hold-note tail still covers the spawn area.
        for n in self.notes:
            if n.lane == lane and n.is_hold and not n.hit and n.y - n.tail_remaining < Note.HEIGHT + 40:
                return True
        return False

    def spawn_note(self, late_ms=0.0):
        # late_ms: how long after its exact beat time we are spawning (frame granularity).
        # The note is started that far down its path so it sits where it would have been
        # had it spawned exactly on the beat. It still starts above the screen (y ~ -30).
        start_y = -30 + self.speed * (late_ms / FRAME_MS)
        free = [l for l in range(LANES) if not self._lane_blocked(l)]
        if not free:
            return False
        lane = random.choice(free)
        if random.random() < HOLD_CHANCE:
            self.notes.append(Note(lane, y=start_y, speed=self.speed, kind=HOLD, hold_frames=HOLD_FRAMES))
        else:
            self.notes.append(Note(lane, y=start_y, speed=self.speed))
        return True

    def _key_down(self, lane):
        # Reliable held-key check (not just KEYDOWN events)
        return bool(pygame.key.get_pressed()[LANE_KEYS[lane]])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                elif not self.game_over:
                    for i, key in enumerate(LANE_KEYS):
                        if event.key == key:
                            self.process_tap(i)
        return True

    def process_tap(self, lane):
        # Find closest note in this lane near hit zone
        best = None
        best_dist = 9999
        for note in self.notes:
            if note.lane == lane and not note.hit and not note.missed and not note.holding:
                dist = abs(note.y + Note.HEIGHT//2 - HIT_Y)
                if dist < best_dist:
                    best_dist = dist
                    best = note
        lane_x = lane * LANE_W + LANE_W // 2
        if best and best_dist <= HIT_WINDOW:
            if best_dist < 8:
                grade, pts = "PERFECT", 300
                col = (255, 220, 0)
            elif best_dist < 18:
                grade, pts = "GREAT", 200
                col = (100, 220, 100)
            else:
                grade, pts = "OK", 100
                col = (180, 180, 255)
            if best.is_hold:
                # Hold note: start holding. Scoring/sound happen only when the full hold completes.
                best.holding = True
                best.grade, best.points, best.color = grade, pts, col
                best.y = HIT_Y - Note.HEIGHT // 2   # pin head on the hit line
                self.feedback.append(["HOLD!", col, 25, lane_x, HIT_Y - 30])
                return
            best.hit = True
            self._count_grade(grade)
            self._play_hit_sound()  # PERFECT / GREAT / OK only; never on MISS
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.score += pts * max(1, self.combo // 5)
            self.feedback.append([grade, col, 40, lane_x, HIT_Y - 30])
        else:
            # Tapping with no note in range: combo breaks and "MISS" is shown (original behaviour),
            # but no note was judged, so it is NOT added to miss_count / accuracy.
            self.combo = 0
            self.feedback.append(["MISS", (220,60,60), 40, lane_x, HIT_Y - 30])

    def _update_hold(self, note):
        lane_x = note.lane * LANE_W + LANE_W // 2
        if self._key_down(note.lane):
            note.held_frames += 1
            if note.held_frames >= note.hold_frames and not note.completed:
                # Completed exactly once: scored, sound, removed via note.hit
                note.completed = True
                note.holding = False
                note.hit = True
                self._count_grade(note.grade)
                self._play_hit_sound()
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                self.score += note.points * max(1, self.combo // 5)
                self.feedback.append([note.grade, note.color, 40, lane_x, HIT_Y - 30])
        else:
            # Released early: hold fails -> one miss, combo reset, no points, no sound.
            # The note keeps falling (greyed out) like a missed normal note.
            note.holding = False
            note.missed = True
            self._register_miss()
            self.feedback.append(["MISS", (220,60,60), 40, lane_x, HIT_Y - 30])

    def update(self, dt_ms=None):
        if self.game_over: return
        if dt_ms is None:
            dt_ms = FRAME_MS
        self.frame += 1
        self.elapsed_ms += min(dt_ms, MAX_DT_MS)

        # Difficulty ramp (note speed only - the BPM itself never changes), driven by elapsed time.
        while self.elapsed_ms >= self.next_speedup_ms:
            self.speed = min(10, self.speed + 0.5)
            self.next_speedup_ms += SPEEDUP_EVERY_MS

        # BPM spawning: spawn one note for every beat boundary that has been reached.
        # Beat n is due at n * BEAT_INTERVAL_MS (multiplication, not repeated addition -> no drift).
        while self.elapsed_ms >= self.next_beat * BEAT_INTERVAL_MS:
            beat_time = self.next_beat * BEAT_INTERVAL_MS
            spawned = self.spawn_note(late_ms=self.elapsed_ms - beat_time)
            self.beat_log.append((self.next_beat, beat_time, self.elapsed_ms, spawned))
            if DEBUG_BPM:
                print(f"beat {self.next_beat:4d}  due {beat_time:9.1f} ms  spawned at {self.elapsed_ms:9.1f} ms  "
                      f"(+{self.elapsed_ms - beat_time:5.1f} ms)  {'note' if spawned else 'skipped: lanes blocked'}")
            self.next_beat += 1

        for note in self.notes:
            if note.holding:
                self._update_hold(note)
                continue
            note.update()
            if not note.hit and not note.missed and note.y + Note.HEIGHT // 2 > HIT_Y + HIT_WINDOW:
                note.missed = True
                self._register_miss()

        self.notes = [n for n in self.notes if not (n.hit or (n.missed and n.y > HEIGHT + 10))]
        self.feedback = [[t,c,ttl-1,x,y] for t,c,ttl,x,y in self.feedback if ttl > 1]

        if self.misses >= 15:
            self.game_over = True

    def _draw_hold(self, note, lx, rect):
        base = LANE_COLORS[note.lane]
        if note.missed:
            base = (90, 90, 100)   # failed / missed hold notes turn grey
        tail_h = int(note.tail_remaining)
        if tail_h > 0:
            tail = pygame.Rect(lx - 16, rect.y - tail_h, 32, tail_h + rect.height // 2)
            tail_col = tuple(c // 2 for c in base) if not note.holding else tuple(min(255, c) for c in base)
            pygame.draw.rect(self.screen, tail_col, tail, border_radius=8)
            pygame.draw.rect(self.screen, base, tail, 2, border_radius=8)
        head = rect.inflate(10, 8)   # wider/taller head with a white outline = "hold me"
        pygame.draw.rect(self.screen, base, head, border_radius=6)
        pygame.draw.rect(self.screen, (255, 255, 255) if not note.missed else (140, 140, 150), head, 3, border_radius=6)
        if note.holding:
            pct = note.held_frames / note.hold_frames
            bar = pygame.Rect(lx - 30, HIT_Y + 22, int(60 * pct), 6)
            pygame.draw.rect(self.screen, (255, 255, 255), bar, border_radius=3)

    def draw(self):
        self.screen.fill(BG)
        # Lane dividers
        for i in range(LANES + 1):
            pygame.draw.line(self.screen, (40,40,60), (i*LANE_W,0), (i*LANE_W,HEIGHT), 1)

        # Hit line
        pygame.draw.line(self.screen, (80,80,100), (0,HIT_Y), (WIDTH,HIT_Y), 2)
        for i in range(LANES):
            lx = i*LANE_W + LANE_W//2
            pygame.draw.rect(self.screen, LANE_COLORS[i],
                pygame.Rect(lx - Note.WIDTH//2, HIT_Y - 12, Note.WIDTH, 24), border_radius=6)
            lbl = self.font.render(LANE_LABELS[i], True, (20,20,20))
            self.screen.blit(lbl, (lx - lbl.get_width()//2, HIT_Y - 10))

        # Notes
        for note in self.notes:
            if note.hit: continue
            lx = note.lane * LANE_W + LANE_W // 2
            rect = note.get_rect(lx)
            if note.is_hold:
                self._draw_hold(note, lx, rect)
                continue
            pygame.draw.rect(self.screen, LANE_COLORS[note.lane], rect, border_radius=5)

        # Feedback
        for text, color, ttl, x, y in self.feedback:
            surf = self.font.render(text, True, color)
            alpha = min(255, ttl * 7)
            surf.set_alpha(alpha)
            self.screen.blit(surf, (x - surf.get_width()//2, y))

        # HUD
        sc = self.font.render(f"Score: {self.score}", True, (220,220,220))
        co = self.font.render(f"Combo: {self.combo}x", True, (255,220,80))
        mi = self.font.render(f"Misses: {self.misses}/15", True, (220,100,100))
        self.screen.blit(sc, (10, 10))
        self.screen.blit(co, (10, 40))
        self.screen.blit(mi, (WIDTH - 170, 10))

        if self.game_over:
            ov = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,160))
            self.screen.blit(ov,(0,0))
            cx = WIDTH // 2
            def line(surf, y):
                self.screen.blit(surf, (cx - surf.get_width() // 2, y))
            line(self.big_font.render("GAME OVER", True, (220, 60, 60)), 110)
            line(self.font.render(f"Final Score: {self.score}", True, (200, 200, 200)), 175)
            line(self.font.render(f"Max Combo: {self.max_combo}x", True, (200, 200, 200)), 207)
            # Grade breakdown
            rows = [
                (f"PERFECT: {self.perfect_count}", (255, 220, 0)),
                (f"GREAT: {self.great_count}", (100, 220, 100)),
                (f"OK: {self.ok_count}", (180, 180, 255)),
                (f"MISS: {self.miss_count}", (220, 60, 60)),
            ]
            y = 265
            for text, color in rows:
                line(self.font.render(text, True, color), y)
                y += 34
            line(self.font.render(f"Accuracy: {self.accuracy():.2f}%", True, (255, 255, 255)), y + 12)
            line(self.font.render("Press R to Restart", True, (160, 160, 160)), y + 75)
        pygame.display.flip()

    def run(self):
        running = True
        dt_ms = FRAME_MS
        while running:
            running = self.handle_events()
            self.update(dt_ms)
            self.draw()
            dt_ms = self.clock.tick(FPS)  # real elapsed ms for the frame just finished
        pygame.quit()
