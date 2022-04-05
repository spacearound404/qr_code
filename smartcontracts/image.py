import os

files = os.listdir('./images')

for index, file in enumerate(files):
    os.rename('./images/' + file, './images/' + str(index + 1) + '.png')

