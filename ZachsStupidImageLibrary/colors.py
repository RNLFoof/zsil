import colorsys
from typing import Union, Tuple, Iterator

import requests
from PIL import Image
from PIL import ImageDraw
from PIL import ImageShow

import random as rando
from statistics import mean
import numpy


def convert1to255(col):
    c = list(col)
    for n, x in enumerate(c):
        c[n] = round(x * 255)
    c = tuple(c)
    return c


def convert255to1(col):
    c = list(col)
    for n, x in enumerate(c):
        c[n] = x / 255
    c = tuple(c)
    return c


def randomwhite(takehuefrom=None):
    if takehuefrom:
        hue = colorsys.rgb_to_hsv(*convert255to1(takehuefrom))[0]
    else:
        hue = None

    if rando.randint(0, 1) and not (hue is not None and (hue < 180 / 360 or hue > 246 / 360)):
        if hue is None:
            hue = rando.uniform(180 / 360, 246 / 360)
        c = colorsys.hsv_to_rgb(
            hue,
            rando.random() * 0.1,
            1 - rando.random() * 0.03,
        )
    else:
        if hue is None:
            hue = rando.random()
        c = colorsys.hsv_to_rgb(
            hue,
            rando.random() * 0.04,
            1 - rando.random() * 0.06,
        )

    c = list(c)
    for n, x in enumerate(c):
        c[n] = round(x * 255)
    c.append(255)
    c = tuple(c)
    return c


def randomblack():
    if rando.randint(0, 1):
        c = colorsys.hsv_to_rgb(
            rando.uniform(180 / 360, 246 / 360),
            rando.random() * 0.1,
            rando.random() * 0.03,
        )
    else:
        c = colorsys.hsv_to_rgb(
            rando.random(),
            rando.random() * 0.05,
            rando.random() * 0.07,
        )

    c = list(c)
    for n, x in enumerate(c):
        c[n] = round(x * 255)
    c.append(255)
    c = tuple(c)
    return c


def mergecolors(col1, col2, amount=None):
    if amount is None:
        amount = rando.uniform(0.4, 0.6)
    newcolor = []
    for n, x in enumerate(col1):
        newcolor.append(round(x * (1 - amount) + col2[n] * amount))
    return tuple(newcolor)


def variantof(col):
    a = None
    if len(col) > 3:
        a = col[3]
        col = col[:3]
    h, s, v = colorsys.hsv_to_rgb(*convert255to1(col))
    choice = rando.randint(0, 2)
    if choice == 0:
        h = (h + rando.random() / 5) % 1
    elif choice == 1:
        s = rando.random()
    else:
        v = rando.random()
    if a is not None:
        return convert1to255((h, s, v, a / 255))
    else:
        return convert1to255((h, s, v))


def color_mind(inp):
    print(inp)
    url = "http://colormind.io/api/"
    data = {
        "model": "default",
        "input": [list(x) if type(x) is tuple else x for x in inp]
    }
    data = str(data).replace("'", '"')
    r = requests.post(url, data=data)
    ret = [tuple(x) for x in r.json()["result"]]
    ret = ret * (1 + len(inp) // 5)
    return ret


def average_color(colors: Union[Iterator | Image.Image], mode: str = "RGBA", alpha: Image.Image = None) -> Tuple[int, ]:
    """Averages out several colors.

    Parameters:
    colors (list | PIL.Image): List of color tuples, or an image.

    Returns:
    tuple: Average color."""

    ret = []
    if isinstance(colors, Image.Image):
        mode = colors.getbands()
        colors = list(colors.getdata())
    mode = mode[:len(colors[0])]

    if hasattr(colors[0],'__iter__'):
        weights = None
        a_band = None
        if alpha is not None:
            alpha_data = alpha.getdata()
            weights = [color / 255 for color in alpha_data]
        elif "A" in mode:
            a_band = mode.find("A")
            weights = [color[a_band] / 255 for color in colors]

        for index, band in zip(range(len(colors[0])), mode):
            if band == "H":
                ret.append(average_hue(colors))
            else:
                if weights is not None:
                    print(set(weights))
                    ret.append(numpy.average(
                        list(x[index] for x in colors),
                        weights=weights
                    ))
                else:
                    ret.append(round(mean(x[index] for x in colors)))

        return tuple(ret)
    else:
        return mean(colors)

def average_hue(colors: Union[Iterator | Image.Image]) -> int:
    """Gets the average hue from several colors. Weighs pixels differently based on their saturation, value, and alpha.

    Parameters:
    colors (list | PIL.Image): List of color tuples, or an image.

    Returns:
    int: Average hue."""
    if isinstance(colors, Image.Image):
        colors = numpy.hstack(colors.convert("HSV").getdata(), colors.getchannel('A').getdata())

    if hasattr(colors[0], '__iter__'):
        weights = []
        for color in colors:
            weights.append(numpy.prod(list(band/255 for band in color[1:])))
        return numpy.average(
            list(color[0] for color in colors),
            weights=weights
        )
    else:
        return mean(colors)


def show_palette(cols, size=64):
    img = Image.new("RGB", (size * len(cols), size))
    draw = ImageDraw.Draw(img)
    for n, x in enumerate(cols):
        draw.rectangle((n * size, 0, (n + 1) * size, size), tuple(x))
    ImageShow.show(img)


def show_palette_cube(cols, divider=2, back=False):
    img = Image.new("RGBA", (256 * 2 // divider, 256 * 3 // divider))
    draw = ImageDraw.Draw(img)

    top = tuple(x // divider for x in (255, 0))
    print(top)
    topleft = tuple(x // divider for x in (0, 127))
    topright = tuple(x // divider for x in (255 * 2, 127))
    center = tuple(x // divider for x in (255, 255))
    bottomleft = tuple(x // divider for x in (0, 255 + 127))
    bottomright = tuple(x // divider for x in (255 * 2, 255 + 127))
    bottom = tuple(x // divider for x in (255, 255 * 2))

    draw.polygon([top, topleft, bottomleft, bottom, bottomright, topright], fill=(128, 128, 128, 32),
                 outline=(0, 0, 0, 255))
    imgdata = img.load()
    multiplier = -1 if back else 1
    for n, rgb in enumerate(sorted(cols, key=lambda c: multiplier * sum(c))):
        r, g, b = rgb[:3]
        # x = round(0 + r + g)
        # y = round(255+127 - r/2 + g/2 - b)
        # x,y = bottom
        # x += r - g
        # y -= r//2 + g // 2 + b
        x, y = center
        x += (-(255 - r) + (255 - g)) // divider
        y += (-(255 - r) // 2 - (255 - g) // 2 + (255 - b)) // divider
        print(x, y)
        imgdata[x, y] = (r, g, b, 255)

    draw.polygon([top, topleft, center, topright], fill=None, outline=(0, 0, 0, 255))
    draw.polygon([topleft, center, bottom, bottomleft], fill=None, outline=(0, 0, 0, 255))
    draw.polygon([topright, center, bottom, bottomright], fill=None, outline=(0, 0, 0, 255))

    ImageShow.show(img)


def get_color_difference(rgb1, rgb2, bands="rgbh"):
    """Returns an increasingly high number the more different two colors are."""
    total = 0
    # RGB
    for n in range(3):
        total += abs(rgb1[n] - rgb2[n])
    total += abs(gethue(rgb1) - gethue(rgb2))
    return total


def gethue(rgb):
    r, g, b = rgb
    maxc = max(r, g, b)
    minc = min(r, g, b)
    v = maxc
    if minc == maxc:
        return 0
    rc = (maxc - r) / (maxc - minc)
    gc = (maxc - g) / (maxc - minc)
    bc = (maxc - b) / (maxc - minc)
    if r == maxc:
        h = bc - gc
    elif g == maxc:
        h = 255 * 2 + rc - bc
    else:
        h = 255 * 4 + gc - rc
    h = (h / 255 * 6) % 255
    return h


def getcolorusage(img):
    """Counts how many times each rgba value is used. Or whatever mode the image is in.

    Parameters:
    img (PIL.Image): The image you want info on.

    Returns:
    dict: rgba(?) as key, quantity as value."""
    imgdata = img.load()
    quantities = {}
    for x in range(img.width):
        for y in range(img.height):
            pixel = imgdata[x, y]
            quantities.setdefault(pixel, 0)
            quantities[pixel] += 1
    return quantities


def getmostcommoncolors(img: Image, fraction=0.1):
    """Returns a list of the most common colors in an image.

    Parameters:
    img (PIL.Image): The image you want info on.
    fraction (float): A decimal between 0 and 1 indicating how far from the most common colors you want.
                      For example, 0.1 returns the fewest colors that, combined, make up 10% of the image.

    Returns:
    list: The most common colors."""
    colorusage = getcolorusage(img)
    totaldesired = img.width * img.height * fraction
    total = 0
    mostcommon = []
    for color, quantity in sorted(colorusage.items(), key=lambda x: -x[1]):
        mostcommon.append(color)
        total += quantity
        if total >= totaldesired:
            break
    return mostcommon


def getmostrepresentativecolors(img: Image, commonfraction=0.1, representativefraction=0.1) -> list[tuple[int, int, int]]:
    """Returns a list of the most "representative" colors in an image, determined by their proximity to the most common
    colors of the image liquid rescaled to half size.

    Parameters:
    img (PIL.Image): The image you want info on.
    commonfraction (float): A decimal between 0 and 1 indicating how far from the most common colors you want.
                      For example, 0.1 returns the fewest colors that, combined, make up 10% of the image.
    representativefraction (float): A decimal between 0 and 1 indicating how far from the most representative colors you want.
                      For example, 0.1 returns the fewest colors that, combined, make up 10% of the image.

    Returns:
    list: The most representative colors."""
    from ZachsStupidImageLibrary.coolstuff import piltowand, wandtopil

    quantities = getcolorusage(img)
    totaldesired = img.width * img.height * representativefraction

    mode = img.mode
    resizedimg = img.copy()
    resizedimg.thumbnail((64, 64))
    # wandimg = piltowand(resizedimg)
    # wandimg.liquid_rescale(width=resizedimg.height//2, height=resizedimg.height//2)
    # resizedimg = wandtopil(wandimg).convert(mode)
    mostcommoncolors = getmostcommoncolors(resizedimg, fraction=commonfraction)

    colornotrepresentativeness = {}  # Increases as a color becomes less representative of the whole
    for color in quantities.keys():
        numofbands = len(color)
        colornotrepresentativeness[color] = 0
        for commoncolor in mostcommoncolors:
            colornotrepresentativeness[color] += get_color_difference(color, commoncolor)

    representativecolors = []
    total = 0
    for color, notrepresentativeness in sorted(colornotrepresentativeness.items()):
        representativecolors.append(color)
        total += quantities[color]
        if total >= totaldesired:
            break
    return representativecolors
