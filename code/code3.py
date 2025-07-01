import pygame
import random
import torch
import torch.nn as nn

# Define DQN model
class DQN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(DQN, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

    def forward(self, x):
        return self.model(x)

# Load the saved model
model_path = "datasets/dqn_snake.pth"

model = DQN(input_size=11, hidden_size=256, output_size=3)  # Adjust based on your setup
model.load_state_dict(torch.load(model_path))
model.eval()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (50, 153, 213)

BLOCK_SIZE = 10

# Function to draw snake with a gradient color and border
def draw_snake(snake_list):
    for idx, segment in enumerate(snake_list):
        # Add a gradient effect to the snake's body
        r = 0 + (idx * 5) % 255  # Gradually increase red color
        g = 255 - (idx * 5) % 255  # Gradually decrease green color
        b = 0  # Keep blue as 0
        color = (r, g, b)
        
        # Draw the snake segment with a border (black color)
        pygame.draw.rect(screen, color, pygame.Rect(segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE), border_radius=3)
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE), 2)  # Border

# Snake Game Environment Class
class SnakeEnv:
    def __init__(self):
        self.width = 780
        self.height = 500
        self.block_size = BLOCK_SIZE
        self.reset()

    def reset(self):
        self.snake = [[100, 100]]
        self.direction = [self.block_size, 0]
        self.score = 0
        self.food = self.place_food()
        self.frame = 0
        return self.get_state()

    def place_food(self):
        while True:
            x = random.randint(0, (self.width - self.block_size) // self.block_size) * self.block_size
            y = random.randint(0, (self.height - self.block_size) // self.block_size) * self.block_size
            if [x, y] not in self.snake:
                return [x, y]

    def step(self, action):
        self.frame += 1
        self.move(action)
        reward = 0
        done = False

        head = self.snake[-1]

        # Check for collision with walls or self (reduce penalty for collision)
        if head in self.snake[:-1] or head[0] < 0 or head[0] >= self.width or head[1] < 0 or head[1] >= self.height:
            done = True
            reward = -5  # Reduced penalty
            return self.get_state(), reward, done

        # Check for collision with food
        if head == self.food:
            self.snake.append(self.food)
            self.score += 1
            reward = 10
            self.food = self.place_food()
        else:
            self.snake.pop(0)

        return self.get_state(), reward, done

    def move(self, action):
        directions = [[self.block_size, 0], [0, self.block_size], [-self.block_size, 0], [0, -self.block_size]]
        idx = directions.index(self.direction)

        if action == 0:
            new_dir = directions[idx]
        elif action == 1:
            new_dir = directions[(idx + 1) % 4]
        elif action == 2:
            new_dir = directions[(idx - 1) % 4]
        else:
            new_dir = self.direction

        self.direction = new_dir
        new_head = [self.snake[-1][0] + new_dir[0], self.snake[-1][1] + new_dir[1]]
        self.snake.append(new_head)

    def get_state(self):
        head = self.snake[-1]
        point_l = [head[0] - self.block_size, head[1]]
        point_r = [head[0] + self.block_size, head[1]]
        point_u = [head[0], head[1] - self.block_size]
        point_d = [head[0], head[1] + self.block_size]

        dir_l = self.direction == [-self.block_size, 0]
        dir_r = self.direction == [self.block_size, 0]
        dir_u = self.direction == [0, -self.block_size]
        dir_d = self.direction == [0, self.block_size]

        state = [
            (self.direction == [self.block_size, 0] and point_r in self.snake or point_r[0] >= self.width) or
            (self.direction == [-self.block_size, 0] and point_l in self.snake or point_l[0] < 0) or
            (self.direction == [0, self.block_size] and point_d in self.snake or point_d[1] >= self.height) or
            (self.direction == [0, -self.block_size] and point_u in self.snake or point_u[1] < 0), 

            (dir_u and (point_r in self.snake or point_r[0] >= self.width)) or
            (dir_d and (point_l in self.snake or point_l[0] < 0)) or
            (dir_l and (point_u in self.snake or point_u[1] < 0)) or
            (dir_r and (point_d in self.snake or point_d[1] >= self.height)),

            (dir_u and (point_l in self.snake or point_l[0] < 0)) or
            (dir_d and (point_r in self.snake or point_r[0] >= self.width)) or
            (dir_l and (point_d in self.snake or point_d[1] >= self.height)) or
            (dir_r and (point_u in self.snake or point_u[1] < 0)), 

            dir_l, dir_r, dir_u, dir_d,

            self.food[0] < head[0],
            self.food[0] > head[0],
            self.food[1] < head[1],
            self.food[1] > head[1],
        ]

        return list(map(int, state))

    def render(self, screen):
        screen.fill((0, 0, 0))  # Fill the screen with black
        draw_snake(self.snake)  # Use the improved snake drawing function
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(self.food[0], self.food[1], self.block_size, self.block_size))  # Draw food
        pygame.display.update()

# Game loop
def game_loop():
    pygame.init()
    global screen
    screen = pygame.display.set_mode((780, 500))
    pygame.display.set_caption("Snake Game with DQN")

    env = SnakeEnv()
    game_over = False
    score = 0

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        state = env.get_state()
        state_tensor = torch.FloatTensor(state).unsqueeze(0)  # Convert state to tensor
        with torch.no_grad():
            action = model(state_tensor).argmax(dim=1).item()  # Choose action from model

        next_state, reward, done = env.step(action)

        if done:
            game_over = True
            print("Game Over! Final Score:", score)

        score += reward

        env.render(screen)  # Render the environment

        # Adjust game speed (slower for an easier game)
        pygame.time.Clock().tick(200)  # Slowed down the speed

    pygame.quit()

# Start the game loop
game_loop()
