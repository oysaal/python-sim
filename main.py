import os
os.environ['SDL_AUDIODRIVER'] = 'dummy' 

import pygame
import sys
import json
import math
import random
from pygame.locals import *

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60
COLORS = {
    'background': (3, 33, 89),
    'text': (255, 255, 255),
    'correct': (0, 255, 0),
    'incorrect': (255, 0, 0),
    'panel': (25, 25, 45)
}

class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load('assets/ship.png').convert_alpha()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//4, SCREEN_HEIGHT//2))
        self.heading = 0  # Degrees (0 = north)
        self.speed = 0.0  # Knots
        self.turning_rate = 1.5  # Degrees per frame

    def update(self):
        # Realistic ship movement physics
        rad = math.radians(self.heading)
        self.rect.x += self.speed * math.cos(rad)
        self.rect.y -= self.speed * math.sin(rad)

        # Rotate ship image
        self.image = pygame.transform.rotate(self.original_image, self.heading)
        self.rect = self.image.get_rect(center=self.rect.center)

class Buoy(pygame.sprite.Sprite):
    def __init__(self, pos, buoy_type):
        super().__init__()
        self.type = buoy_type
        self.image = pygame.image.load(f'assets/buoys/{buoy_type}.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)

class MarineSimulator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Marine Navigation Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 48)

        self.load_questions()
        self.init_game()

    def load_questions(self):
        with open('questions.json') as f:
            self.questions = json.load(f)
        self.current_level = 'Cadet'
        self.current_question = 0
        self.score = 0

    def init_game(self):
        self.ship = Ship()
        self.buoys = pygame.sprite.Group()
        self.other_vessels = pygame.sprite.Group()
        self.generate_question()

    def generate_question(self):
        if self.current_question >= len(self.questions[self.current_level]):
            self.current_question = 0
        q = self.questions[self.current_level][self.current_question]

        # Generate environment
        self.buoys.empty()
        if 'green' in q['scenario'].lower():
            self.buoys.add(Buoy((1000, 400), 'green_conical'))
        elif 'red' in q['scenario'].lower():
            self.buoys.add(Buoy((1000, 400), 'red_can'))

        self.question_text = q['scenario']
        self.options = q['options']
        self.correct_answer = q['correct']
        self.rule = q['rule']

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_1: self.check_answer(0)
                if event.key == K_2: self.check_answer(1)
                if event.key == K_3 and len(self.options) > 2: self.check_answer(2)

    def check_answer(self, selected):
        if selected == self.correct_answer:
            self.score += 1
            feedback_color = COLORS['correct']
        else:
            feedback_color = COLORS['incorrect']

        self.show_feedback(feedback_color)
        self.current_question += 1
        self.generate_question()

    def show_feedback(self, color):
        feedback_surf = pygame.Surface((800, 200))
        feedback_surf.fill(COLORS['panel'])
        text = self.font.render(f"Rule: {self.rule}", True, color)
        feedback_surf.blit(text, (20, 20))
        self.screen.blit(feedback_surf, (240, 500))
        pygame.display.update()
        pygame.time.wait(2000)

    def draw_hud(self):
        # Speed and heading
        speed_text = self.font.render(f"Speed: {self.ship.speed:.1f} kts", True, COLORS['text'])
        heading_text = self.font.render(f"Heading: {self.ship.heading:.0f}°", True, COLORS['text'])
        self.screen.blit(speed_text, (20, 20))
        self.screen.blit(heading_text, (20, 60))

        # Question panel
        panel = pygame.Surface((800, 200))
        panel.fill(COLORS['panel'])
        text = self.big_font.render(self.question_text, True, COLORS['text'])
        panel.blit(text, (20, 20))

        for i, option in enumerate(self.options):
            text = self.font.render(f"{i+1}. {option}", True, COLORS['text'])
            panel.blit(text, (20, 80 + i*40))

        self.screen.blit(panel, (240, 500))

    def check_collisions(self):
        collisions = pygame.sprite.spritecollide(self.ship, self.buoys, False)
        if collisions:
            buoy = collisions[0]
            if (buoy.type == 'green_conical' and buoy.rect.centerx < self.ship.rect.centerx) or \
               (buoy.type == 'red_can' and buoy.rect.centerx > self.ship.rect.centerx):
                self.score -= 2  # Penalize wrong side passing

    def run(self):
        while True:
            self.screen.fill(COLORS['background'])
            self.handle_input()

            # Ship controls
            keys = pygame.key.get_pressed()
            if keys[K_RIGHT]:
                self.ship.heading += self.ship.turning_rate
            if keys[K_LEFT]:
                self.ship.heading -= self.ship.turning_rate
            if keys[K_UP]:
                self.ship.speed = min(20, self.ship.speed + 0.1)
            if keys[K_DOWN]:
                self.ship.speed = max(0, self.ship.speed - 0.2)

            self.ship.update()
            self.check_collisions()

            # Draw elements
            self.screen.blit(self.ship.image, self.ship.rect)
            self.buoys.draw(self.screen)
            self.draw_hud()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    simulator = MarineSimulator()
    simulator.run()