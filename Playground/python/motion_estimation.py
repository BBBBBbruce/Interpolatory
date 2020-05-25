import numpy as np
import math
from imageio import imread, imwrite
import sys
import cProfile

def get_motion_vectors_fs(block_size, target_region, source_frame, target_frame):
    output = np.empty_like(source_frame, dtype='float64')

    for s_row in range(0, source_frame.shape[0], block_size):
        for s_col in range(0, source_frame.shape[1], block_size):

            source_block = source_frame[s_row:s_row+block_size, s_col:s_col+block_size, :]
            lowest_sad = block_size * block_size * (255 + 255 + 255) + 1    # maximum sad score for a block
            lowest_distance = block_size ** 2
            target_index = (0, 0)
            for t_row in range(max(0, s_row - math.floor(target_region/2)), min(target_frame.shape[0] - block_size, s_row + math.floor(target_region/2))):
                for t_col in range(max(0, s_col - math.floor(target_region/2)), min(target_frame.shape[1] - block_size, s_col + math.floor(target_region/2))):
                    target_block = target_frame[t_row:t_row+source_block.shape[0], t_col:t_col+source_block.shape[1], :]
                    sad = np.sum(np.abs(np.subtract(source_block, target_block)))
                    distance = ((s_row - t_row) ** 2) + ((s_col - t_col) ** 2)
                    if (sad < lowest_sad) or (sad == lowest_sad and distance < lowest_distance):
                        lowest_distance = distance
                        lowest_sad = sad
                        target_index = (t_row, t_col)
            block = np.full((source_block.shape[0], source_block.shape[1], 3), [target_index[0] - s_row, target_index[1] - s_col, lowest_sad])
            output[s_row:s_row+source_block.shape[0], s_col:s_col+source_block.shape[1], :] = block

    return output

if __name__ == "__main__":
    if sys.argv[1] == '-f':
        csv_path = sys.argv[2]
        image_height = int(sys.argv[3])
        image_width = int(sys.argv[4])
        out_path = sys.argv[5]
        output = np.genfromtxt(csv_path, delimiter=',').reshape((image_height, image_width, 3))
    else:
        block_size = int(sys.argv[1])
        region = int(sys.argv[2])
        im1 = imread(sys.argv[3])[:,:,:3]
        im2 = imread(sys.argv[4])[:,:,:3]
        out_path = sys.argv[5]
        output = get_motion_vectors(block_size, region, im1, im2)
        np.savetxt(out_path + "/out.csv", output.reshape(-1), delimiter=',')

    output_intensity = np.copy(output)
    max_intensity = 0
    for i in range(output_intensity.shape[0]):
        for j in range(output_intensity.shape[1]):
            intensity = float(output_intensity[i,j,0]) ** 2.0 + float(output_intensity[i,j,1]) ** 2.0
            if intensity > max_intensity:
                max_intensity = intensity
            output_intensity[i,j,:] = [intensity, intensity, intensity]
    output_intensity = 255 - (output_intensity * (255.0 / float(max_intensity)))
    imwrite(out_path + "/out_intensity.png", output_intensity)



# im1 = imread("../interpolation-samples/still_frames/eg1/frame1.png")[:,:,:3]
# im2 = imread("../interpolation-samples/still_frames/eg1/frame2.png")[:,:,:3]
# cProfile.run('get_motion_vectors(40, 300, im1, im2)')