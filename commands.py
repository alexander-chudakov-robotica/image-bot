from PIL import Image, ImageEnhance

def run(msg, path):
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

    def interpret(stack, image):
        index = 0
        def pop():
            nonlocal index
            nonlocal stack
            index += 1
            return stack[index - 1]

        region = [None, None, None, None]

        while index < len(stack):
            mappedRegion = (
                0 if region[0] is None else region[0],
                0 if region[1] is None else region[1],
                image.width if region[2] is None else region[2],
                image.height if region[3] is None else region[3],
            )
            localImage = image.crop(mappedRegion)
            match pop():
                case "x1" | "y1" | "x2" | "y2" as variable:
                    value = pop()
                    if value == "default":
                        value = None
                    else:
                        value = int(value)
                    region[("x1", "y1", "x2", "y2").index(variable)] = value 
                    
                case "sharp":
                    localImage = ImageEnhance.Sharpness(localImage).enhance(int(pop()))
                case "brightness":
                    localImage = ImageEnhance.Brightness(localImage).enhance(int(pop()))
                case "contrast":
                    localImage = ImageEnhance.Contrast(localImage).enhance(int(pop()))
            image.paste(localImage, mappedRegion[:2])
        return image
                

    stack = parse(msg)
    image = Image.open(path)
    image = interpret(stack, image)
    image.show()
