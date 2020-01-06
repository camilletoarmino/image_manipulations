# Preprocessing
import cv2
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse
from tqdm import tqdm


def preprocess_image(image, args):
    """
    Parameters
    ----------
    file : str
        Name of image data file
    args : class
        Arguments for preprocessing
    """
    plt.close('all')

    # Get full path
    img_path = os.path.join(args.input_dir, image)
    
    # Read image
    img = cv2.imread(img_path)
    
    # Convert to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    
    # Remove noise with bilateral filter (effective in noise removal while keeping edges sharp)
    gray_img_filt = cv2.bilateralFilter(gray_img, d=7, sigmaColor=75, sigmaSpace=75)
    
    # Remove shadows from image by blurring image and subtracting from non-blurred image
    dilated_img = cv2.dilate(gray_img_filt, kernel=np.ones((20, 20), np.uint8))
    blur_img = cv2.medianBlur(dilated_img, ksize=21)
    diff_img = 255 - cv2.absdiff(gray_img_filt, blur_img)
    
    # Threshold image
    maxValue = 255
    if args.threshold_type == 'simple':
        # Apply simple thresholding
        _, thresh_img = cv2.threshold(diff_img, args.threshold_value, maxValue, cv2.THRESH_BINARY)
    elif args.threshold_type == 'otsu':
        # Apply Otsu Binarization, which searches for a threshold based on the local minima in a
        # bi-modal histogram
        _, thresh_img = cv2.threshold(diff_img, 0, maxValue, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Save image
    plt.imshow(thresh_img)
    save_filename = os.path.join(args.output_dir, image)
    cv2.imwrite(save_filename, thresh_img) 


def parse_args():
    """
    Arguments required for preprocessing decisions
    The defaults are set for simple thresholding.
    To perform otsu, change the threshold type and 
    set the threshold value to None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, 
                        help="The directory where the files are that need preprocessing", required=True)
    parser.add_argument("--output_dir", type=str, 
                        help="The directory where the preprocessed images should be saved", required=True)
    parser.add_argument("--threshold_type", type=str,
                        help="Either simple or otsu threshold", default='simple',
                        choices=['simple', 'otsu'])
    parser.add_argument("--threshold_value", type=int, 
                        help="Threshold value for simple thresholding: \
                              anything greater than the value will turn white, \
                              anything less than the value will turn black",
                        default=190)
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
            preprocess_image(image, args)
    else:
        for image in tqdm(image_files):
            preprocess_image(image, args)
