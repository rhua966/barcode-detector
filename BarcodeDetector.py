from matplotlib import pyplot
from matplotlib.patches import Rectangle

from ImageProcessor import *

import png
import argparse


def readRGBImageToSeparatePixelArrays(input_filename):
    '''
    Reads an RGB color png file and returns width, height, as well as pixel arrays for r,g,b
    '''

    image_reader = png.Reader(filename=input_filename)
    (image_width, image_height, rgb_image_rows, rgb_image_info) = image_reader.read()

    print(f"Read image {input_filename} width={image_width}, height={image_height}")

    # Pixel arrays are lists of lists, where each inner list stores one row of greyscale pixels
    pixel_array_r = []
    pixel_array_g = []
    pixel_array_b = []

    for row in rgb_image_rows:
        pixel_row_r = []
        pixel_row_g = []
        pixel_row_b = []
        r = 0
        g = 0
        b = 0
        for elem in range(len(row)):
            # RGB triplets are stored consecutively in image_rows
            if elem % 3 == 0:
                r = row[elem]
            elif elem % 3 == 1:
                g = row[elem]
            else:
                b = row[elem]
                pixel_row_r.append(r)
                pixel_row_g.append(g)
                pixel_row_b.append(b)

        pixel_array_r.append(pixel_row_r)
        pixel_array_g.append(pixel_row_g)
        pixel_array_b.append(pixel_row_b)

    return (image_width, image_height, pixel_array_r, pixel_array_g, pixel_array_b)

def writeGreyscalePixelArraytoPNG(output_filename, pixel_array, image_width, image_height):
    """
    Write the greyscale pixel_array to output_filename.
    """

    with open(output_filename, 'wb') as file:
        writer = png.Writer(image_width, image_height, greyscale=True)
        writer.write(file, pixel_array)

def run(input_filename):

    fig1, axs1 = pyplot.subplots(3, 2)
   
    (image_width, image_height, px_array_r, px_array_g, px_array_b) = readRGBImageToSeparatePixelArrays(input_filename)

    px_array = ImageProcessor.computeRGBToGreyscale(px_array_r, px_array_g, px_array_b, image_width, image_height)
    px_array = ImageProcessor.scaleTo0And255AndQuantize(px_array, image_width, image_height)

    axs1[0, 0].set_title('Input greyscale image')
    axs1[0, 0].imshow(px_array, cmap='gray') 

    horizontal_edges = ImageProcessor.computeHorizontalEdgesSobelAbsolute(px_array, image_width, image_height)
    horizontal_edges = ImageProcessor.scaleTo0And255AndQuantize(horizontal_edges, image_width, image_height)
    vertical_edges = ImageProcessor.computeVerticalEdgesSobelAbsolute(px_array, image_width, image_height)
    vertical_edges = ImageProcessor.scaleTo0And255AndQuantize(vertical_edges, image_width, image_height)
    edges = ImageProcessor.computeStrongVerticalEdgesBySubtractingHorizontal(vertical_edges, horizontal_edges, image_width, image_height)
    edges = ImageProcessor.scaleTo0And255AndQuantize(edges, image_width, image_height)
    
    n = 10
    averaged_edges = edges
    for i in range(n):
        averaged_edges = ImageProcessor.computeBoxAveraging3x3(averaged_edges, image_width, image_height)
    averaged_edges = ImageProcessor.scaleTo0And255AndQuantize(averaged_edges, image_width, image_height)

    axs1[0, 1].set_title('Averaged edge image')
    axs1[0, 1].imshow(averaged_edges, cmap='gray')

    threshold_value = 70
    thresholded = ImageProcessor.computeThresholdGE(averaged_edges, threshold_value, image_width, image_height)

    axs1[1, 0].set_title('Thresholded image')
    axs1[1, 0].imshow(thresholded, cmap='gray')

    eroded = thresholded
    for i in range(n):
        eroded = ImageProcessor.computeErosion8Nbh3x3FlatSE(eroded, image_width, image_height)
    dilated = eroded
    for i in range(n):
        dilated = ImageProcessor.computeDilation8Nbh3x3FlatSE(dilated, image_width, image_height)

    axs1[1, 1].set_title('Morphologically processed image')
    axs1[1, 1].imshow(dilated, cmap='gray')

    (cclabeled, size_dict_cc) = ImageProcessor.computeConnectedComponentLabeling(dilated, image_width, image_height)
    (final_labeled, (bbox_min_x, bbox_max_x, bbox_min_y, bbox_max_y)) = ImageProcessor.determineLargestConnectedComponent(cclabeled, size_dict_cc, image_width, image_height)

    axs1[2, 0].set_title('Largest detected component')
    axs1[2, 0].imshow(final_labeled, cmap='gray')

    print(f"bbox {bbox_min_x} {bbox_max_x} {bbox_min_y} {bbox_max_y}")


    # Draw the bounding box as a rectangle into the original input image
    axs1[2, 1].set_title('Final image of detection')
    axs1[2, 1].imshow(px_array, cmap='gray')
    rect = Rectangle((bbox_min_x, bbox_min_y), bbox_max_x - bbox_min_x, bbox_max_y - bbox_min_y, linewidth=3, edgecolor='g', facecolor='none')
    axs1[2, 1].add_patch(rect)

    # plot the current figure
    pyplot.show()

def main():
    parser = argparse.ArgumentParser(description='Barcode Detection')
    parser.add_argument("--file", "-f", type=str, required=True)
    args = parser.parse_args()

    filename = f"./images/{args.file}"
    print(filename)
    run(filename)

if __name__ == "__main__":
    main()




