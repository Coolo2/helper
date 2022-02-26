
from typing import Tuple

from PIL import Image, ImageOps, ImageEnhance

__all__ = ('Colour', 'ColourTuple', 'DefaultColours', 'deepfry')

Colour = Tuple[int, int, int]
ColourTuple = Tuple[Colour, Colour]


class DefaultColours:
    red = ((254, 0, 2), (255, 255, 15))
    blue = ((36, 113, 229), (255,) * 3)


async def deepfry(img: Image, *, colours: ColourTuple = DefaultColours.red) -> Image:

    img = img.copy().convert('RGB')

    img = img.convert('RGB')
    width, height = img.width, img.height
    img = img.resize((int(width ** .75), int(height ** .75)), resample=Image.LANCZOS)
    img = img.resize((int(width ** .88), int(height ** .88)), resample=Image.BILINEAR)
    img = img.resize((int(width ** .9), int(height ** .9)), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, 4)

    r = img.split()[0]
    r = ImageEnhance.Contrast(r).enhance(2.0)
    r = ImageEnhance.Brightness(r).enhance(1.5)

    r = ImageOps.colorize(r, colours[0], colours[1])

    img = Image.blend(img, r, 0.75)
    img = ImageEnhance.Sharpness(img).enhance(100.0)

    return img

async def blurpify(img : Image):

    img : Image = img.convert('RGBA')
    pixels = img.getdata()
    newData = []

    for pixel in pixels:
        avgColor = (pixel[0]+pixel[1]+pixel[2]) / 3

        if avgColor < 105:
            newData.append((114, 137, 218, 255))
        else:
            newData.append((255, 255, 255, 255))
    
    img.putdata(newData)
    
    return img