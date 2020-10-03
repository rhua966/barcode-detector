import sys

from Queue import Queue

class ImageProcessor:

    @staticmethod
    def createInitializedGreyscalePixelArray(image_width, image_height, initValue=0):
        """
        Create a height by width array of init_value
        E.g. 
        width, height = 2, 3 will
        return [[0, 0],
                [0, 0],
                [0, 0]]
        """

        new_array = []
        for row in range(image_height):
            new_row = []
            for col in range(image_width):
                new_row.append(initValue)
            new_array.append(new_row)

        return new_array

    @staticmethod
    def computeMinAndMaxValues(pixel_array, image_width, image_height):
        """
        Compute the min and max greyvalue.
        """

        # Initialization
        min_value = sys.maxsize
        max_value = -min_value

        for y in range(image_height):
            for x in range(image_width):
                if pixel_array[y][x] < min_value:
                    min_value = pixel_array[y][x]
                if pixel_array[y][x] > max_value:
                    max_value = pixel_array[y][x]

        return(min_value, max_value)

    @staticmethod
    def computeRGBToGreyscale(pixel_array_r, pixel_array_g, pixel_array_b, image_width, image_height):
        """
        Convert a rgb image to greyscale
        """

        greyscale_pixel_array = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)

        for i in range(image_height):
            for j in range(image_width):

                # g = 0.299r + 0.587g + 0.114b
                greyscale_pixel_array[i][j] = round(0.299 * pixel_array_r[i][j] + 0.587 * pixel_array_g[i][j] + 0.114 * pixel_array_b[i][j])

        return greyscale_pixel_array

    @staticmethod
    def scaleTo0And255AndQuantize(pixel_array, image_width, image_height):
        """
        Perform contrast stretching on the pixel_array from min and max to the full 8 bit range 0-255
        """

        new_pixel_array = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)
        min_val, max_val = ImageProcessor.computeMinAndMaxValues(pixel_array, image_width, image_height)
        if max_val == min_val:
            return new_pixel_array
        
        for i in range(image_height):
            for j in range(image_width):
                
                s = int(round((pixel_array[i][j]-min_val)*255/(max_val-min_val)))
                if s > 255:
                    s = 255
                if s < 0:
                    s = 0
                new_pixel_array[i][j] = s

        return new_pixel_array

    @staticmethod
    def computeVerticalEdgesSobelAbsolute(pixel_array, image_width, image_height):
        """
        Compute vertical edges using Sobel kernel ignoring border pixels
        0.125 * [[-1  0  1]
                [-2  0  2]
                [-1  0  1]]
        """

        gradient = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)

        for i in range(1, image_height-1):
            for j in range(1, image_width-1):
                
                dx = 0.125 * (-pixel_array[i - 1][j - 1] - 2 * pixel_array[i][j - 1] - pixel_array[i + 1][j - 1] +\
                            pixel_array[i - 1][j + 1] + 2 * pixel_array[i][j + 1] + pixel_array[i + 1][j + 1])
                gradient[i][j] = dx if dx >= 0 else -dx
                
        return gradient

    @staticmethod
    def computeHorizontalEdgesSobelAbsolute(pixel_array, image_width, image_height):

        """
        Compute horizontal edges using Sobel kernel ignoring border pixels
        0.125 * [[ 1  2  1]
                [ 0  0  0]
                [-1 -2 -1]]
        """

        gradient = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)

        for i in range(1, image_height-1):
            for j in range(1, image_width-1):
                
                dy = 0.125 * (pixel_array[i - 1][j - 1] + 2 * pixel_array[i - 1][j] + pixel_array[i - 1][j + 1] - \
                            pixel_array[i + 1][j - 1] - 2 * pixel_array[i + 1][j] - pixel_array[i + 1][j + 1])
                gradient[i][j] = dy if dy >= 0 else -dy
                
        return gradient
    @staticmethod
    def computeStrongVerticalEdgesBySubtractingHorizontal(vertical_edges, horizontal_edges, image_width, image_height):

        """
        Takes vertical and horizontal edges as input and substracts horizontal from vertical.
        Set to 0 if the result is less then 0.
        """

        strongVer = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)
        
        for i in range(0, image_height):
            for j in range(0, image_width):
                
                s = vertical_edges[i][j] - horizontal_edges[i][j]
                strongVer[i][j] = max(0, s)
    
        return strongVer

    @staticmethod
    def computeBoxAveraging3x3(pixel_array, image_width, image_height):

        """
        Find a blured image using a 3 by 3 mean filter ignoring border pixel
        1/9 * [[ 1  2  1]
            [ 1  1  1]
            [ 1  1  1]]
        """

        blured = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)

        for i in range(1, image_height-1):
            for j in range(1, image_width - 1):
                
                avg = (1 / 9) * (pixel_array[i - 1][j - 1] + pixel_array[i - 1][j] + pixel_array[i - 1][j + 1] +\
                            pixel_array[i][j - 1] + pixel_array[i][j] + pixel_array[i][j + 1] +\
                            pixel_array[i + 1][j - 1] + pixel_array[i + 1][j] + pixel_array[i + 1][j + 1])
                blured[i][j] = avg

        return blured

    @staticmethod
    def computeThresholdGE(pixel_array, threshold_value, image_width, image_height):
        """
        Compute a thresholded binary picture with only 0 or 255, 
        if the input pixel is strictly small than the threshold value set it to 0, otherwise 255.
        """

        thresholded = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)

        for i in range(image_height):
            for j in range(image_width):
                if pixel_array[i][j] >= threshold_value:
                    val = 255
                else:
                    val = 0
                thresholded[i][j] = val
        
        return thresholded

    @staticmethod
    def computeErosion8Nbh3x3FlatSE(pixel_array, image_width, image_height):
        """
        Compute Morphological Erosion using a flat 8-neighbourhood structing element of size 3 by 3.
        Ignoring border pixels.
        """

        eroded = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)

        for x in range(1, image_height-1):
            for y in range(1, image_width-1):
                
                if (pixel_array[x-1][y-1] == 0) or (pixel_array[x-1][y] == 0) or (pixel_array[x-1][y+1] == 0) or \
                    (pixel_array[x][y-1] == 0) or (pixel_array[x][y] == 0) or (pixel_array[x][y+1] == 0) or \
                    (pixel_array[x+1][y-1] == 0) or (pixel_array[x+1][y] == 0) or (pixel_array[x+1][y+1] == 0):
                    
                    eroded[x][y] = 0
                else:
                    eroded[x][y] = 1

        return eroded

    @staticmethod
    def computeDilation8Nbh3x3FlatSE(pixel_array, image_width, image_height):
        """
        Compute Morphological Dilation using a flat 8-neighbourhood structing element of size 3 by 3.
        """
        
        dilated = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)

        # Fill border with 0
        for i in range(image_height):
            pixel_array[i].append(0)
            pixel_array[i].insert(0, 0)
        pixel_array.append([0] *(image_width + 2))
        pixel_array.insert(0, [0] * (image_width + 2))
        
        
        for x in range(1, image_height+1):
            for y in range(1, image_width+1):
                    
                
                if (pixel_array[x-1][y-1] != 0) or (pixel_array[x-1][y] != 0) or (pixel_array[x-1][y+1] != 0) or\
                    (pixel_array[x][y-1] != 0) or (pixel_array[x][y] != 0) or (pixel_array[x][y+1] != 0) or\
                    (pixel_array[x+1][y-1] != 0) or (pixel_array[x+1][y] != 0) or (pixel_array[x+1][y+1] != 0):
                    
                    dilated[x-1][y-1] = 1
                else:
                    dilated[x-1][y-1] = 0

        return dilated

    @staticmethod
    def computeConnectedComponentLabeling(pixel_array, image_width, image_height):
        """
        Takes a binary pixel_array and performs a single pass queue-based connected component labeling algorithm
        """

        # def dfs(x, y, old, new, val, label):
        #     if (x<0) or (y<0) or (x>=image_height) or (y>=image_width) or (old[x][y]==0) or (new[x][y] != 0):
        #         return 0
        #     count = 1
        #     old[x][y] = 0
        #     new[x][y] = label
            
        #     count += dfs(x-1, y, old, new, val, label)
        #     count += dfs(x+1, y, old, new, val, label)
        #     count += dfs(x, y-1, old, new, val, label)
        #     count += dfs(x, y+1, old, new, val, label)
        #     return count
        
        # label = 1
        # d = {}
        # old = pixel_array
        # new = [[0 for _ in range(image_width)] for _ in range(image_height)]
        # for x in range(image_height):
        #     for y in range(image_width):
        #         if old[x][y] != 0:
        #             d[label] = dfs(x, y, old, new, old[x][y], label)
        #             label += 1
                    
        # return new, d
        
        label = 1
        d = {}
        old = pixel_array
        new = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)
        visited = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)
        
        for x in range(image_height):
            for y in range(image_width):
                
                if old[x][y] != 0 and visited[x][y] == 0:  # Find a pixel yet not visited
                    count = 0
                    q = Queue()
                    q.enqueue((x,y))  # Add to the queue
                    
                    while not q.isEmpty():
                        (a, b) = q.dequeue()
                        new[a][b] = label
                        visited[a][b] = 1
                        count += 1
                        
                        # Visit neighbouring pixels that haven't visited
                        if (b-1 >= 0) and (old[a][b-1] != 0) and (visited[a][b-1] == 0):
                            q.enqueue((a,b-1))
                            visited[a][b-1] = 1
                        if (b+1 < image_width) and (old[a][b+1] != 0) and (visited[a][b+1] == 0):
                            q.enqueue((a,b+1))
                            visited[a][b+1] = 1
                        if (a-1 >= 0) and (old[a-1][b] != 0) and (visited[a-1][b] == 0):
                            q.enqueue((a-1,b))
                            visited[a-1][b] = 1
                        if (a+1 < image_height) and (old[a+1][b] != 0) and (visited[a+1][b] == 0):
                            q.enqueue((a+1,b))
                            visited[a+1][b] = 1
                    
                    # Finished counting the current component region, set the dictionary
                    d[label] = count
                    label += 1

        return new, d

    @staticmethod
    def determineLargestConnectedComponent(cclabeled, label_size_dictionary, image_width, image_height):
        """
        Find the bounding box (rect) for the largest connected component.
        """

        final_labeled = ImageProcessor.createInitializedGreyscalePixelArray(image_width, image_height)

        size_of_largest_component = 0
        label_of_largest_component = 0
        for lbl_i in label_size_dictionary.keys():
            if label_size_dictionary[lbl_i] > size_of_largest_component:
                size_of_largest_component = label_size_dictionary[lbl_i]
                label_of_largest_component = lbl_i

        print("label of largest component: ", label_of_largest_component)

        # determine bounding box of the largest component only
        bbox_min_x = image_width
        bbox_min_y = image_height
        bbox_max_x = 0
        bbox_max_y = 0
        for y in range(image_height):
            for x in range(image_width):
                if cclabeled[y][x] == label_of_largest_component:
                    final_labeled[y][x] = 255
                    if x < bbox_min_x:
                        bbox_min_x = x
                    if y < bbox_min_y:
                        bbox_min_y = y
                    if x > bbox_max_x:
                        bbox_max_x = x
                    if y > bbox_max_y:
                        bbox_max_y = y
                else:
                    final_labeled[y][x] = 0

        return (final_labeled, (bbox_min_x, bbox_max_x, bbox_min_y, bbox_max_y))