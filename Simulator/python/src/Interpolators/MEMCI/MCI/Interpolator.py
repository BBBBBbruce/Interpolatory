import imageio
import math
import time
import numpy as np
from io import BytesIO
from fractions import Fraction

import sys

from ....util import eprint

sys.path.append('.')

from ..ME.full_search import get_motion_vectors as get_motion_vectors_fs
from ..ME.tss import get_motion_vectors as get_motion_vectors_tss
from decimal import Decimal
from copy import deepcopy
# from Globals import debug_flags
# from VideoStream import BenchmarkVideoStream, VideoStream
import matplotlib.pyplot as plt
from ..smoothing.threeXthree_mv_smoothing import smooth
from ..smoothing.median_filter import median_filter
from ..smoothing.mean_filter import mean_filter
from ..smoothing.weighted_mean_filter import weighted_mean_filter
from ..ME.hbma import get_motion_vectors as hbma
from ...base import BaseInterpolator
from .Unidirectional_2 import UniDir2Interpolator
'''
blends frames
'''


def blend_frames(frames, weights):
    return np.average(frames, axis=0, weights=weights).astype(np.uint8, copy=False)

'''
MEMCI using full search for ME and uniderictional
MCI with median filter for filling holes.



'''
ME_dict={
    "full":get_motion_vectors_fs,
    "tss":get_motion_vectors_tss,
    "HBMA":hbma
}
smoothing_dict={
    "mean":mean_filter,
    "median":median_filter,
    "weighted":weighted_mean_filter

}
class UniDirInterpolator(BaseInterpolator):
    def __init__(self, target_fps,video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)

        ### TODO:- charles etc., here, you will need to specify the default args
        ### then, following rrin/sepconv, assign new args
        ### i'll do block_size for now

        self.block_size = 8
        # print('sup bro set block_size here')
        # self.blockSize = block_size
        self.target_region = 7
        self.me_mode = ME_dict["HBMA"]
        # print(self.me_mode)
        self.filter_mode = smoothing_dict["weighted"]
        self.filterSize = 4
        self.sub_region = 1
        self.steps_HBMA = 4
        self.min_block_size = 4

        print(self.block_size)
        if hasattr(args, 'block_size'):
            self.block_size = args['block_size']
        if hasattr(args, 'target_region'):
            self.target_region = args['target_region']
        if hasattr(args, 'me_mode'):
            self.me_mode = ME_dict[ args['me_mode']]
        if hasattr(args, 'filter_mode'):
            self.filter_mode = smoothing_dict[args['filter_mode']]



    ### this function should be only self, idx, like in BaseInterpolator
    def get_interpolated_frame(self, idx):

        self.MV_field_idx= -1 #Index in source video that the current motion field is based on.
        self.MV_field=[]
        #for arg, value in args.items():
         #   setattr(self, arg, value)
        #print("the block size used was:", self.blockSize)
    # def get_interpolated_frame(self, idx, b, t):
        #source_frame is the previous frame in the source vidoe.
        source_frame_idx = math.floor(idx/self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)
        #print(source_frame_idx)
        #Normalized distance from current_frame to the source frame.
        dist = idx/self.rate_ratio - math.floor(idx/self.rate_ratio)

        #If the frame to be interpolated is coinciding with a source frame.
        if dist == 0:
            return source_frame


        #Check if the frame to be interpolated is between the two frames
        #that the current motion field is estimated on.
        if not self.MV_field_idx < idx/self.rate_ratio < self.MV_field_idx+1:
            target_frame = self.video_stream.get_frame(source_frame_idx+1)
            # print(self.me_mode)
            if(self.me_mode!=hbma):

                self.me_mode = ME_dict[self.me_mode]
                self.MV_field= self.me_mode(self.block_size,self.target_region,source_frame,target_frame)
            else:

                print("here")
                self.MV_field= self.me_mode(self.block_size,self.target_region,self.sub_region,self.steps_HBMA,self.min_block_size,source_frame,target_frame)

            # print("Begin smoothing")
            self.MV_field = smooth(self.filter_mode,self.MV_field,self.filterSize)
            self.MV_field_idx = source_frame_idx


            #Uncomment if you want to plot vector field when running benchmark.py
            #self.plot_vector_field(block_size,steps, source_frame)




        #Initialize new frame
        Interpolated_Frame =  np.ones(source_frame.shape)*-1
        #Matrix with lowest sad value fo every interpolated pixel.
        SAD_interpolated_frame = np.full([source_frame.shape[0],source_frame.shape[1]],np.inf)

        #Follow motion vectorcs to obtain interpolated pixel Values
        #If interpolated frame has multiple values, take the one with lowest SAD.
        for u in range(0, source_frame.shape[0]):
            for v in range(0, source_frame.shape[1]):

                #Get the new coordinates by following scaled MV.
                u_i = int(u + round(self.MV_field[u,v,0]*dist))
                v_i = int(v + round(self.MV_field[u,v,1]*dist))
                # print("u_i ",u_i," v_i ",v_i)
                if(u_i<source_frame.shape[0] and v_i<source_frame.shape[1]):
                    if  self.MV_field[u,v,2] <= SAD_interpolated_frame[u_i, v_i]:

                        Interpolated_Frame[u_i, v_i] =  source_frame[u, v]
                        SAD_interpolated_frame[u_i, v_i] = self.MV_field[u,v,2]
                else:
                    Interpolated_Frame[u, v] = source_frame[u, v]
                    SAD_interpolated_frame[u, v] = self.MV_field[u, v, 2]

        # New_Interpolated_Frame = smooth(mean_filter, self.MV_field, 10)

        #Run median filter over empty pixels in the interpolated frame.
        k=10 #Median filter size = (2k+1)x(2k+1)
        #Bad implementation. Did not find any 3d median filter
        # that can be applied to specific pixels.
        New_Interpolated_Frame = np.copy(Interpolated_Frame)
        for u in range(0, Interpolated_Frame.shape[0]):
            for v in range(0, Interpolated_Frame.shape[1]):
                if Interpolated_Frame[u,v,0] == -1:
                    #to make sure the hole is not empty
                    Interpolated_Frame[u, v] = source_frame[u, v]
                    SAD_interpolated_frame[u, v] = self.MV_field[u, v, 2]

                    u_min=max(0,u-k)
                    u_max=min(Interpolated_Frame.shape[0],u+k+1)
                    v_min=max(0,v-k)
                    v_max=min(Interpolated_Frame.shape[1],v+k+1)
                    New_Interpolated_Frame[u,v,0] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,0])
                    New_Interpolated_Frame[u,v,1] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,1])
                    New_Interpolated_Frame[u,v,2] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,2])

        New_Interpolated_Frame = New_Interpolated_Frame.astype(source_frame.dtype)

        # print(self.filterSize,self.smoothing_filter,self.me_mode,self.target_region,self.blockSize)
        return New_Interpolated_Frame
    def __str__(self):
        return 'uniMEMCI'




'''
%
%   e.g. 24->60
%   A A A B B C C    C D D
%
%   e.g. 25->30
%   A A B C D E F
%
'''



# class Bi(BaseInterpolator):
#     def __init___(self, target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2,
#                   **args):
#         super().__init__(target_fps, video_in_path,
#                          video_out_path, max_out_frames, max_cache_size)

    # def get_interpolated_frame(self, idx):
    #     self.blockSize = int(block_size)
    #     self.target_region = int(target_region)
    #     self.me_mode = ME_dict[ME_mode]
    #     self.smoothing_filter = smoothing_dict[filter_mode]
    #     self.filterSize = int(filter_size)
    #
    #
    #     self.MV_field_idx= -1 #Index in source video that the current motion field is based on.
    #     self.MV_field=[]
    #     #for arg, value in args.items():
    #     #    setattr(self, arg, value)
    #     source_frame_idx = math.floor(idx / self.rate_ratio)
    #     source_frame = self.video_stream.get_frame(source_frame_idx)
    #
    #     dist = idx / self.rate_ratio - math.floor(idx / self.rate_ratio)
    #
    #     if dist == 0:
    #         return source_frame
    #
    #     if not self.MV_field_idx < idx / self.rate_ratio < self.MV_field_idx + 1:
    #         target_frame = self.video_stream.get_frame(source_frame_idx + 1)
    #         # self.MV_field = get_motion_vectors(4, 10, source_frame, target_frame)
    #         self.MV_field_idx = source_frame_idx
    #
    #         self.MV_field = self.me_mode(self.blockSize, self.target_region, source_frame, target_frame)
    #         bwd = self.me_mode(self.blockSize, self.target_region, target_frame, source_frame)
    #         self.MV_field = smooth(self.smoothing_filter,self.MV_field,self.filterSize)
    #         bwd = smooth(self.smoothing_filter,bwd,self.filterSize)
    #
    #     Interpolated_Frame = np.ones(source_frame.shape, dtype='float64') * -1
    #     SAD_interpolated_frame = np.full([source_frame.shape[0], source_frame.shape[1]], np.inf)
    #
    #     for u in range(0, source_frame.shape[0]):
    #         for v in range(0, source_frame.shape[1]):
    #             if self.MV_field[u, v, 2] > bwd[u, v, 2]:
    #                 dist = 1.0 - dist
    #                 u_i = int(u + round(bwd[u, v, 0] * dist))
    #                 v_i = int(v + round(bwd[u, v, 1] * dist))
    #                 if(u_i<source_frame.shape[0] and v_i<source_frame.shape[1]):
    #
    #                     if bwd[u, v, 2] <= SAD_interpolated_frame[u_i, v_i]:
    #                         Interpolated_Frame[u_i, v_i] = target_frame[u, v]
    #                         SAD_interpolated_frame[u_i, v_i] = bwd[u, v, 2]
    #                         self.MV_field[u, v] = bwd[u, v]
    #
    #                     # self.MV_field[u,v,0] = bwd[u,v,0]
    #                     # self.MV_field[u,v,1] = bwd[u,v,1]
    #                     # self.MV_field[u,v,2] = bwd[u,v,2]
    #
    #             else:
    #                 u_i = int(u + round(self.MV_field[u, v, 0] * dist))
    #                 v_i = int(v + round(self.MV_field[u, v, 1] * dist))
    #                 if(u_i<source_frame.shape[0] and v_i<source_frame.shape[1]):
    #                     if self.MV_field[u, v, 2] <= SAD_interpolated_frame[u_i, v_i]:
    #                         Interpolated_Frame[u_i, v_i] = source_frame[u, v]
    #                         SAD_interpolated_frame[u_i, v_i] = self.MV_field[u, v, 2]
    #     k=10
    #     New_Interpolated_Frame = np.copy(Interpolated_Frame)
    #     for u in range(0, Interpolated_Frame.shape[0]):
    #         for v in range(0, Interpolated_Frame.shape[1]):
    #             if Interpolated_Frame[u,v,0] == -1:
    #                 u_min=max(0,u-k)
    #                 u_max=min(Interpolated_Frame.shape[0],u+k+1)
    #                 v_min=max(0,v-k)
    #                 v_max=min(Interpolated_Frame.shape[1],v+k+1)
    #                 New_Interpolated_Frame[u,v,0] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,0])
    #                 New_Interpolated_Frame[u,v,1] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,1])
    #                 New_Interpolated_Frame[u,v,2] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,2])
    #
    #     New_Interpolated_Frame = New_Interpolated_Frame.astype(source_frame.dtype)
    #
    #     # print(self.filterSize,self.smoothing_filter,self.me_mode,self.target_region,self.blockSize)
    #     return New_Interpolated_Frame
    #
    # def __str__(self):
    #     return 'BI'


class BiDirInterpolator(BaseInterpolator):
    def __init__(self, target_fps,video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):

        super().__init__(target_fps, video_in_path,
                         video_out_path, max_out_frames, max_cache_size)
        self.block_size = 8
        # self.blockSize = block_size
        self.target_region = 7
        self.me_mode = 'HBMA'
        self.filter_mode = "weighted"
        self.filterSize = 4
        self.sub_region = 1
        self.steps_HBMA = 4
        self.min_block_size = 4


        if hasattr(args, 'block_size'):
            self.block_size = args['block_size']
        if hasattr(args, 'target_region'):
            self.target_region = args['target_region']
        if hasattr(args, 'me_mode'):
            self.me_mode = args['me_mode']
        if hasattr(args, 'filter_mode'):
            self.filter_mode = args['filter_mode']


    def get_interpolated_frame(self, idx):

        self.MV_field_idx= -1 #Index in source video that the current motion field is based on.
        self.MV_field=[]
        #for arg, value in args.items():
        #    setattr(self, arg, value)
        source_frame_idx = math.floor(idx / self.rate_ratio)
        source_frame = self.video_stream.get_frame(source_frame_idx)

        dist = idx / self.rate_ratio - math.floor(idx / self.rate_ratio)

        if dist == 0:
            return source_frame

        if not self.MV_field_idx < idx / self.rate_ratio < self.MV_field_idx + 1:
            target_frame = self.video_stream.get_frame(source_frame_idx + 1)
            # self.MV_field = get_motion_vectors(4, 10, source_frame, target_frame)
            self.MV_field_idx = source_frame_idx

            self.MV_field = self.me_mode(self.block_size, self.target_region, source_frame, target_frame)
            bwd = self.me_mode(self.block_size, self.target_region, target_frame, source_frame)
            self.MV_field = smooth(self.filter_mode,self.MV_field,self.filterSize)
            bwd = smooth(self.filter_mode,bwd,self.filterSize)

        Interpolated_Frame = np.ones(source_frame.shape, dtype='float64') * -1
        SAD_interpolated_frame = np.full([source_frame.shape[0], source_frame.shape[1]], np.inf)

        for u in range(0, source_frame.shape[0]):
            for v in range(0, source_frame.shape[1]):
                if self.MV_field[u, v, 2] > bwd[u, v, 2]:
                    dist = 1.0 - dist
                    u_i = int(u + round(bwd[u, v, 0] * dist))
                    v_i = int(v + round(bwd[u, v, 1] * dist))
                    if(u_i<source_frame.shape[0] and v_i<source_frame.shape[1]):

                        if bwd[u, v, 2] <= SAD_interpolated_frame[u_i, v_i]:
                            Interpolated_Frame[u_i, v_i] = target_frame[u, v]
                            SAD_interpolated_frame[u_i, v_i] = bwd[u, v, 2]
                            self.MV_field[u, v] = bwd[u, v]

                        # self.MV_field[u,v,0] = bwd[u,v,0]
                        # self.MV_field[u,v,1] = bwd[u,v,1]
                        # self.MV_field[u,v,2] = bwd[u,v,2]

                else:
                    u_i = int(u + round(self.MV_field[u, v, 0] * dist))
                    v_i = int(v + round(self.MV_field[u, v, 1] * dist))
                    if(u_i<source_frame.shape[0] and v_i<source_frame.shape[1]):
                        if self.MV_field[u, v, 2] <= SAD_interpolated_frame[u_i, v_i]:
                            Interpolated_Frame[u_i, v_i] = source_frame[u, v]
                            SAD_interpolated_frame[u_i, v_i] = self.MV_field[u, v, 2]
        k=10
        New_Interpolated_Frame = np.copy(Interpolated_Frame)
        for u in range(0, Interpolated_Frame.shape[0]):
            for v in range(0, Interpolated_Frame.shape[1]):
                if Interpolated_Frame[u,v,0] == -1:
                    u_min=max(0,u-k)
                    u_max=min(Interpolated_Frame.shape[0],u+k+1)
                    v_min=max(0,v-k)
                    v_max=min(Interpolated_Frame.shape[1],v+k+1)
                    New_Interpolated_Frame[u,v,0] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,0])
                    New_Interpolated_Frame[u,v,1] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,1])
                    New_Interpolated_Frame[u,v,2] = np.median(Interpolated_Frame[u_min:u_max,v_min:v_max,2])

        New_Interpolated_Frame = New_Interpolated_Frame.astype(source_frame.dtype)

        # print(self.filterSize,self.smoothing_filter,self.me_mode,self.target_region,self.blockSize)
        return New_Interpolated_Frame

    def __str__(self):
        return 'bwMEMCI'

def MEMCI (target_fps, video_in_path=None, video_out_path=None, max_out_frames=math.inf, max_cache_size=2, **args):
    mci_mode = 'unidir'
    print(args)
    if 'mci_mode' in args:
        mci_mode = args['mci_mode']

    if (mci_mode == 'unidir'):
        return UniDirInterpolator(target_fps, video_in_path, video_out_path, max_out_frames, max_cache_size,**args)
    elif (mci_mode == 'bidir'):
        return BiDirInterpolator(target_fps, video_in_path, video_out_path, max_out_frames, max_cache_size,**args)
    elif (mci_mode == 'unidir2'):
        return UniDir2Interpolator(target_fps, video_in_path, video_out_path, max_out_frames, max_cache_size,**args)
    else:
        eprint(f'Unknown RRIN flow_usage_method argument: {mci_mode}')
        exit(1)