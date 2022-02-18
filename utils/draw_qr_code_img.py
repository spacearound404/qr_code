import os
import random
import config
from PIL import Image, ImageDraw


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def draw_qr_code_by_percentage(percentage=0):
    arr = []
    black_pix_max_count = config.QRCODE_IMG_PIXEL_COUNT * percentage / 100

    im = Image.new('RGB', (100, 100), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    for i in range(config.QRCODE_IMG_PIXEL_COUNT):
        if i <= black_pix_max_count:
            arr.append(1)
        else:
            arr.append(0)

    random.shuffle(arr)

    matrix = list(chunks(arr, 100))

    for y in range(100):
        for x in range(100):
            if matrix[x][y] == 0:
                draw.point(
                    xy=(
                        (x, y)
                    ), fill='white'
                )
            else:
                draw.point(
                    xy=(
                        (x, y)
                    ), fill='black'
                )

    os.remove(config.QRCODE_IMG_PATH)

    im.save(config.QRCODE_IMG_PATH, quality=config.QRCODE_IMG_RESOLUTION)
