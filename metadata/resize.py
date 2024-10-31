def resize_image(image):
    width, height = image.size

    left = (width - height)/2
    top = 0
    right = (width + height)/2
    bottom = height

    im = image.crop((left, top, right, bottom))
    return im