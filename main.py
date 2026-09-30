import telebot
from telebot import util
from pathlib import Path
from PIL import Image, ImageEnhance

import commands
import config

# bot = telebot.TeleBot(config.key)

FILE_LIMIT = 500 * 10**3

cachedir = "CacheDir"

def getImageDirs(id):
    path = Path(f"{cachedir}/imageCache/{id}")
    path.mkdir(parents=True, exist_ok=True)
    return path

#@bot.message_handler(commands=["imagels"])
def handler1(m):
    imageDir = getImageDirs(m.from_user.id)
    message = """
_______________________
<name> - <size>:
***********************
"""
    diskUsage = 0
    if not any(imageDir.iterdir()):
        message += " - (no uploaded images...)\n"
    else:
        for item in imageDir.iterdir():
            if not item.is_file():
                continue
            message += f" - {item.name} - {item.stat().st_size}\n"
            diskUsage += item.stat().st_size
    message += f"""
=======================
Space: {diskUsage}/{FILE_LIMIT} bytes
=======================
"""
    #bot.send_message(m.chat.id, message)
    print(message)

#@bot.message_handler(commands=["imagerm"])
def handler2(m):
    imageDir = getImageDirs(m.from_user.id)
    fileName = util.extract_arguments(m.text)
    file = imageDir / fileName
    if file.is_file():
        print(f'OK) Deleted "{fileName}".')
        file.unlink()
    else:
        print(f'BAD) "{fileName}" does not exist.')

#@bot.message_handler(commands=["imagerun"])
def handler3(m):
    def parse(msg):
        def strspn(msg, target, reverse = False):
            index = 0
            while index < len(msg) and (msg[index] in target) == (not reverse):
                index += 1
            return index

        WHITESPACE = " \t\n"

        index = 0
        stack = []
        tokenEnd = None

        while True:
            index += strspn(msg[index:], WHITESPACE)
            if index >= len(msg):
                break
            tokenEnd = index + strspn(msg[index:], WHITESPACE, reverse = True)
            stack.append(msg[index:tokenEnd])
            index = tokenEnd

        return stack

    def interpret(stack, imageDir):
        index = 0
        def pop():
            nonlocal index
            nonlocal stack
            index += 1
            return stack[index - 1]

        region = [None, None, None, None]
        image = None
        imagePath = None
        while index < len(stack):
            update = False

            if image != None:
                localImage = image.crop(mappedRegion)
            match pop():
                case "image":
                    if image != None:
                        image.save(imagePath)
                    imagePath = imageDir / str(pop())
                    image = Image.open(imagePath)
                    localImage = None

                    mappedRegion = (
                        0 if region[0] is None else region[0],
                        0 if region[1] is None else region[1],
                        image.width if region[2] is None else region[2],
                        image.height if region[3] is None else region[3],
                    )
                case "x1" | "y1" | "x2" | "y2" as variable:
                    value = pop()
                    if value == "default":
                        value = None
                    else:
                        value = int(value)
                    region[("x1", "y1", "x2", "y2").index(variable)] = value 
                case "sharp":
                    localImage = ImageEnhance.Sharpness(localImage).enhance(int(pop()))
                    update = True
                case "brightness":
                    localImage = ImageEnhance.Brightness(localImage).enhance(int(pop()))
                    update = True
                case "contrast":
                    localImage = ImageEnhance.Contrast(localImage).enhance(int(pop()))
                    update = True
            if update:
                update = False
                image.paste(localImage, mappedRegion[2:])

        image.save(imagePath)
                
    imageDir = getImageDirs(m.from_user.id)
    stack = parse(util.extract_arguments(m.text))
    interpret(stack, imageDir)

class FakeMessage:
    class from_user:
        id = 1234567890
    class chat:
        id = 9876543210
    text = "/imagerun image image2.jpg sharp 10 x1 100 brightness 10"

handler3(FakeMessage)

bot.infinity_polling()
