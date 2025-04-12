from textwrap import TextWrapper
from google import genai
from google.genai import types
import PIL.Image
import cv2
import numpy
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
from gtts import gTTS
import time
import pygame
import pyperclip
from pygame.locals import *

# image = PIL.Image.open("z.jpeg")
client = genai.Client(api_key=sys.argv[1])
past = 'text.txt'
pygame.mixer.init()
video = cv2.VideoCapture(0)
wrapper = TextWrapper(width = 60)
wrapper2 = TextWrapper(width = 64)
class Button:
    def __init__(self, pos, size, filename, colorMain, colorBorder):
        self.img = pygame.image.load(filename)
        self.colorMain = colorMain
        self.colorBorder = colorBorder
        self.colorTemp = colorBorder
        self.redefine(pos, size)
        
    def draw(self):
        pygame.draw.rect(App.screen, self.colorMain, self.rect, 0, 10)
        pygame.draw.rect(App.screen, self.colorBorder, self.rect, 5, 10)
        App.screen.blit(self.display, self.imgRect)

    def redefine(self, pos, size):
        self.pos = pos
        self.display = pygame.transform.scale(self.img, (size[0]/2, size[1]))
        self.rect = Rect(pos[0], pos[1], size[0], size[1])
        self.imgRect = Rect(pos[0] + size[0]/4, pos[1], size[0], size[1])
        
    def check_press(self, pos):
        if self.rect.collidepoint(*pos):
            
            return True
        return False

class Text:
    def __init__(self, text, pos, **options):
        self.text = text
        self.pos = pos
        self.fontname = 'Monaco.ttf'
        self.fontsize = 15
        self.fontcolor = Color('black')
        self.set_font()
        self.render()

    def set_font(self):
        # """Set the font from its name and size."""
        self.font = pygame.font.Font(self.fontname, self.fontsize)

    def render(self):
        self.img = self.font.render(self.text, True, self.fontcolor)
        self.rect = self.img.get_rect()
        self.rect.topleft = self.pos
        
    def draw(self):
        App.screen.blit(self.img, self.rect)

        
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Peaky Blinders CRE[AT]E App')
        pygame.display.set_icon(pygame.image.load('img.jpeg'))
        flags = RESIZABLE
        App.screen = pygame.display.set_mode((640, 640), flags)
        App.running = True
        App.response = 'nothing yet'
        App.responseArray = [self.response]
        App.img = pygame.surface.Surface((50, 50))
        App.img.fill(Color('black'))
        App.capture = Button((500, 10), (130, 65), 'video.png', (0, 255, 0), (0, 200, 0))
        App.speak = Button((500, 85), (130, 65), 'audio.png', (200, 200, 255), (150, 150, 200))
        App.copy = Button((500, 160), (130, 65), 'copy.png', (200, 200, 200), (150, 150, 150))
        App.edit = Button((500, 235), (130, 65), 'edit.png', (100, 100, 255), (50, 50, 255))
        App.quit = Button((500, 310), (130, 65), 'quit.png', (255, 0, 0), (200, 0, 0))
        App.resize = pygame.transform.scale(App.img, (480, 270))
        App.slide = 0
        App.prompt = ''
        App.delete = False
        App.deleteTick = 0
        App.deleteSpeed = 45
        App.recording = True
        try:
            with open('prompt.txt', 'r') as file:
                App.prompt = file.read()
        except Exception as e:
            print(f'An error occurred: {e}')
            App.prompt = ('If there are whiteboards, write down what is written on the board.' +
                        'If there are diagrams, describe the diagrams.' + 
                        'If there are no diagrams or boards, resond with \"None detected\"')
        App.promptArray = wrapper2.wrap(App.prompt)
    def run(self):
        while App.running:
            App.deleteTick += 1
            for event in pygame.event.get():
                if event.type == QUIT:
                    App.running = False
                elif event.type == pygame.KEYDOWN:
                    if App.slide == 0:
                        if event.key == pygame.K_SPACE:
                            App.takePhoto()
                    elif event.key == pygame.K_ESCAPE:
                        App.slide = 0
                    elif event.key == pygame.K_BACKSPACE:
                        App.deleteTick = 0
                        App.delete = True
                    elif event.key >= 32 and event.key <= 126:
                        App.prompt += chr(event.key)
                elif event.type == VIDEORESIZE:
                    width, height = event.size
                    changed = False
                    if width < 320:
                        width = 320
                        changed = True
                    if height < 5/8 * width - 15:
                        height = 5/8 * width - 15
                        changed = True
                    if changed:
                        App.screen = pygame.display.set_mode((width,height), HWSURFACE|DOUBLEBUF|RESIZABLE)
                    App.capture.redefine((width * 3/4 + 20, 10), (width/4 - 30, (width/4 - 30)/2))
                    App.speak.redefine((width * 3/4 + 20, (width/4 - 30)/2 + 20), (width/4 - 30, (width/4 - 30)/2))
                    App.copy.redefine((width * 3/4 + 20, (width/4 - 30) + 30), (width/4 - 30, (width/4 - 30)/2))
                    App.edit.redefine((width * 3/4 + 20, 3/2 * (width/4 - 30) + 40), (width/4 - 30, (width/4 - 30)/2))
                    App.quit.redefine((width * 3/4 + 20, 2 * (width/4 - 30) + 50), (width/4 - 30, (width/4 - 30)/2))
                    wrapper = TextWrapper(width = pygame.display.get_surface().get_width() * 3 // 40)
                    App.responseArray = wrapper.wrap(App.response)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if App.capture.check_press(event.pos):
                        if App.recording:
                            App.recording = False
                            App.takePhoto()
                        else:
                            App.recording = True
                    elif App.speak.check_press(event.pos):
                        App.read(App.response)
                    elif App.copy.check_press(event.pos):
                        pyperclip.copy(App.response)
                    elif App.edit.check_press(event.pos):
                        App.slide = 1
                    if App.quit.check_press(event.pos):
                        App.running = False
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_BACKSPACE:
                        App.delete = False
                        App.deleteSpeed = 45
            if App.slide == 0:
                App.displayNormal()
            elif App.slide == 1:
                App.displayEdit()
            pygame.display.update()
            if App.deleteTick >= 60:
                App.deleteTick -= 60
        pygame.quit()

    def displayEdit():
        App.screen.fill((230, 230, 230))
        Text('Welcome to Edit Mode!', pos = (20, 10)).draw()
        Text('Press [Esc] to return home.', pos = (20, 30)).draw()
        Text('Edit the prompt sent to the AI:', pos = (20, 50)).draw()
        width = pygame.display.get_surface().get_width()
        wrapper2 = TextWrapper(width = width // 10)
        App.promptArray = wrapper2.wrap(App.prompt)
        index = 0
        for i in App.promptArray:
            index += 1
            Text(i, pos = (20, 50 + index * 20)).draw()
        if App.deleteSpeed < 5:
            App.deleteSpeed = 5
        if App.delete and App.deleteTick % App.deleteSpeed == 0:
            App.prompt = App.prompt[:-1]
            App.deleteSpeed -= 1
            if App.deleteSpeed < 5:
                App.deleteSpeed = 5
        
    def displayNormal():
        App.screen.fill((230, 230, 230))
        width = pygame.display.get_surface().get_width()
        if App.recording:
            App.record()
        App.resize = pygame.transform.scale(App.img, (width * 3/4, width * 27/64))
        App.screen.blit(App.resize, (10, 10))
        pygame.draw.rect(App.screen, (0,0,0), Rect(10, 10, width * 3/4, width * 27/64), 5)

        App.capture.draw()
        App.speak.draw()
        App.copy.draw()
        App.edit.draw()
        App.quit.draw()

        # Text
        pygame.draw.rect(App.screen, (255,255,255), Rect(10, width * 27/64 + 20, width * 3/4, len(App.responseArray) * 20 + 13), 0, 10)
        pygame.draw.rect(App.screen, (200,200,200), Rect(10, width * 27/64 + 20, width * 3/4, len(App.responseArray) * 20 + 13), 5, 10)
        index = 0
        for i in App.responseArray:
            index += 1
            Text(i, pos = (20, width * 27/64 + 7 + index * 20)).draw()

    def takePhoto():
        App.response, App.img = App.summarize()
        try:
            with open('history.txt', 'a') as file:
                file.write(App.response + '\n')
        except Exception as e:
            print(f'An error occurred: {e}')
        # Read it outloud
        # App.read(App.response)
        wrapper = TextWrapper(width = pygame.display.get_surface().get_width() * 3 // 40)
        App.responseArray = wrapper.wrap(App.response)

    def pilImageToSurface(pilImage):
        return pygame.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode).convert()
    
    def record():
        ret, frame = video.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(frame_rgb)
        App.img = App.pilImageToSurface(image)
        
    def summarize():
        ret, frame = video.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(frame_rgb)
        response = client.models.generate_content(
            model = 'gemini-2.0-flash', contents = [App.prompt, image]
        )
        return response.text, App.pilImageToSurface(image)
    
    def read(words):
        myobj = gTTS(text = words, lang='en', slow=False)
        myobj.save('text.mp3')
        pygame.mixer.music.load('text.mp3')
        pygame.mixer.music.play()
    
   


if __name__ == '__main__':
    App().run()
    try:
        with open('prompt.txt', 'w') as file:
            file.write(App.prompt)
    except Exception as e:
        print(f'An error occurred: {e}')

