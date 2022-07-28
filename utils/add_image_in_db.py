import os
import config


def set_images_path(Image):
    images_is_sent_false = Image.count(is_sent=False)
    images_is_sent_true = Image.count(is_sent=True)

    if (images_is_sent_false + images_is_sent_true) != 0:
        return None

    images_file = os.listdir(config.IMAGES_FOLDER)

    for image_file in images_file:
        Image.add(file_name=f'/{image_file}', is_sent=False)





