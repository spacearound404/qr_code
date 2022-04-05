import os

files = os.listdir('./images')

for file in files:
    if int(file.replace('.png', '')) > 10000:
        os.remove('./images/' + file)
