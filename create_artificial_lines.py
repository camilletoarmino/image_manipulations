import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import os
import random
from tqdm import tqdm
import argparse


def get_params(args):
    """
    Sets line parameters
    
    Returns
    -------
    graph_params : dict
        Dictionary containing set params
    """
    graph_params = dict()
    
    if args.line_color is None: 
        colors = ['r', 'b', 'k']  # red, blue, black
    else:
        colors = args.line_color
    
    if args.line_width is None:
        line_width = [3, 4]
    else:
        line_width = [args.line_width, args.line_width]
        
    graph_params["color_choice"] = random.choice(colors)
    graph_params["line_width"] = random.uniform(line_width[0], line_width[1])
    graph_params["make_graph"] = random.choice([0,1])
    
    return graph_params


def get_num_lines(single_character, y_max, x_max, graph_params):
    
    # determine the number of lines based on the size
    if not single_character:
        if y_max < 90:
            num_lines = random.randint(2,2)
        elif y_max >= 90 and y_max < 200:
            num_lines = random.randint(2,3)
        elif y_max >= 200 and y_max < 300:
            num_lines = random.randint(3,4)
        elif y_max >= 300 and y_max < 400:
            num_lines = random.randint(3,5)
        else:
            num_lines = random.randint(5,7)
    elif single_character:
        # single characters have special conditions
        graph_params["line_width"] = random.uniform(10,13)
        num_lines = random.randint(1,3)

    return num_lines


def add_slants(ys):

    # sometimes the lined should be slanted slightly for more realistic data
    slant_rand = random.randint(1,100)
    if slant_rand <= 40:
        slanted = True
        slant_amount = random.randint(5,15)
        slant_dir_rand = random.randint(1,100)
        if slant_dir_rand <= 50:
            slant_direction = 'up'
        else:
            slant_direction = 'down'
    else:
        slanted = False 
    
    # make lined paper
    slanted_ys = []
    for num in ys:
        # add slants
        if slanted:
            if slant_direction == 'up': 
                num2 = num + slant_amount
            else:
                num2 = num - slant_amount
        # no slant
        else:
            num2 = num
        slanted_ys.append(num2)

    return slanted_ys


def add_lines(image, args):
    
    plt.close('all')

    # get graph params
    graph_params = get_params(args)
    
    # get image path
    img_path = os.path.join(args.input_dir, image)
    
    # read in image
    im = Image.open(img_path)

    # if the image is narrower than it is tall, it is likely to be a single
    # character and should be treated differently
    x_max, y_max = im.size
    single_character = x_max < y_max
    
    # determine the number of lines
    num_lines = get_num_lines(single_character, y_max, x_max, graph_params)

    # get some start and stop values for linear spacing
    # subtracted 10 because it is getting cut off to be
    # at the ymax when saving
    start = (y_max/num_lines) - 10
    stop = y_max - 10

    # make y values
    ys = np.linspace(start, stop, num=num_lines)

    # add slants
    ys_end = add_slants(ys)
    
    # plot lined paper
    for idx in range(0, len(ys)):
        plt.plot([0, x_max], [ys[idx],ys_end[idx]], 'k-', lw=graph_params["line_width"], color=graph_params[ "color_choice" ])

    # make the lined paper into graph paper
    if graph_params["make_graph"]:
       
       # add some noise for where to begin and end the line spacing
        if not single_character:
            start = random.randint(0,10)
            stop = x_max
        else:
            start = (x_max/num_lines) - 10
            stop = x_max - 10
        
        # get the size ratio of the image to compute the number of vertical
        # lines for graph paper
        # TODO: find a better way to make the squares so that they are always
        # square and not rectangular
        x_to_y_ratio = x_max/y_max 
        xs = np.linspace(start, stop, num=round(num_lines*x_to_y_ratio))
        for num in xs:
            plt.plot([num, num], [0,y_max], 'k-', lw=graph_params["line_width"], color=graph_params[ "color_choice" ])

    # save fig
    plt.axis('off')
    plt.imshow(im, cmap='Greys_r')
    filename = os.path.join(args.output_dir, image)
    plt.margins(0,0)
    plt.tight_layout(pad=0)
    plt.savefig(filename, bbox_inches="tight", pad_inches=0)


def parse_args():
    """
    Arguments required for preprocessing decisions
    The defaults are set for simple thresholding.
    To perform otsu, change the threshold type and 
    set the threshold value to None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, 
                        help="The directory where the files are that need lines", required=True)
    parser.add_argument("--output_dir", type=str, 
                        help="The directory where the lines/graph images should be saved", required=True)
    parser.add_argument("--line_color", type=str,
                        help="Denotes color of the lines, if None: randomizes line color from preset \
                              selection", default='k')
    parser.add_argument("--line_width", type=int,
                        help="Denotes the width of the lines per image, if None: randomizes line width from \
                              preset selection", default=None)
    parser.add_argument("--quick_test", type=bool,
                        help="Takes a boolean value: if true, then \
                              only one image is processed and plotted, \
                              if false, all are processed",
                        default=True, choices=[True, False])
    return parser.parse_args()


if __name__ == "__main__":
    
    args = parse_args()

    # make output directory if one does not exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # quick test allows you to see how the manipulation
    # worked and everything is being saved appropriately
    image_files = os.listdir(args.input_dir)

    if args.quick_test == True:
        for image in image_files[0:1]:
            add_lines(image, args)
    else:
        for image in tqdm(image_files):
            add_lines(image, args)
