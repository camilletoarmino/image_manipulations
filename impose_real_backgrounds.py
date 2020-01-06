from PIL import Image
from tqdm import tqdm
import os
import random
import matplotlib.pyplot as plt
import cv2
import argparse
import numpy as np


def change_handwriting_color(image, args):
    
    img_path = os.path.join(args.handwriting_dir, image)
    img = Image.open(img_path)

    if args.add_handwriting_colors is True:

        # get potential colors
        colors = ['red', 'black', 'blue', 'pencil']
        color_selection = random.choice(colors)
        
        # ensure black and white first
        thresh = 110
        maxValue = 255
        img = img.point(lambda p: p > thresh and maxValue)
        
        # change img into numpy array for pixel color manipulation
        data = np.array(img)
        red, green, blue, _ = data.T

        # replace black pixels with selected color
        black_areas = (red == 0) & (green == 0) & (blue == 0)
        
        if color_selection == 'red':
            data[..., :-1][black_areas.T] = (239, 0, 0)
        elif color_selection == 'blue':
            data[..., :-1][black_areas.T] = (34,34,183)
        elif color_selection == 'black':
            pass
        elif color_selection == 'pencil':
            data[..., :-1][black_areas.T] = (105,105,105)
        
        img = Image.fromarray(data)
        
    return img


def add_background(image, args, background_files):
    
    plt.close('all')
    
    handwriting_img = change_handwriting_color(image, args)

    # pick one of the background files randomly
    selected_background = random.choice(background_files)
    background = Image.open(os.path.join(args.backgrounds_dir, selected_background))
    
    # background size --- make sure background are very big
    background_width, background_height = background.size
    
    # sometimes crop the background to get rid of the side lines on lined paper
    rand_background = random.randint(1,100)
    if rand_background >= 20:
        left = 800
        top = 800
        right = background_width
        bottom = background_height
        background = background.crop((left, top, right, bottom))

    # get cropped background size
    background_width, background_height = background.size
    
    # get handwriting image size
    img_width, img_height = handwriting_img.size

    # setting the points for cropped image to match handwriting size
    left = 0
    top = 0
    right = img_width
    bottom = img_height

    # crop image to above dimension  
    background = background.crop((left, top, right, bottom)) 
    
    # paste handwriting image onto background
    background.paste(handwriting_img, (0, 0), handwriting_img)

    # save image
    plt.imshow(background)
    plt.axis('off') 
    save_filename = os.path.join(args.output_dir, os.path.splitext(image)[0]) + '.jpg'
    plt.savefig(save_filename, bbox_inches='tight', pad_inches=0)


def parse_args():
    """
    Arguments required for preprocessing decisions
    The defaults are set for simple thresholding.
    To perform otsu, change the threshold type and 
    set the threshold value to None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--handwriting_dir", type=str, 
                        help="The directory where the synthetic handwriting png files are - must be pngs", required=True)
    parser.add_argument("--backgrounds_dir", type=str, 
                        help="The directory where the real background files are", required=True)
    parser.add_argument("--output_dir", type=str, 
                        help="The directory where the superimposed images should be saved", required=True)
    parser.add_argument("--add_handwriting_colors", type=bool,
                        help="If True, randomly choose from 4 different colors to simulate different colored \
                              pens and pencils", default=False)
    parser.add_argument("--quick_test", type=bool,
                        help="Takes a boolean value: if true, then \
                              only one image is processed and plotted, \
                              if false, all are processed",
                        default=True)
    return parser.parse_args()


if __name__ == "__main__":
    
    args = parse_args()

    # make output directory if one does not exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # dump files
    handwriting_files = [file for file in os.listdir(args.handwriting_dir) if file.endswith('.png')]
    background_files = [file for file in os.listdir(args.backgrounds_dir) if file.endswith('.jpg')]

    if args.quick_test == True:
        for image in handwriting_files[0:1]:
            add_background(image, args, background_files)
    else:
        for image in tqdm(handwriting_files):
            add_background(image, args, background_files)
