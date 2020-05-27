import sys
import json
import os

sys.path.append('./src')
from src import util, Interpolator, Benchmark, Globals
from src.Interpolator import InterpolatorDictionary
from src.Benchmark import benchmark, get_middle_frame

mode_flag = None

if (len(sys.argv) > 1):
    args = sys.argv[1:]
    mode_flag = args[0]

    # if the last flag is -gui
    # turn off debugs
    last_arg = args[len(args) - 1]
    if (last_arg == '-gui'):
        # turn off debugs
        for flag in Globals.debug_flags:
            Globals.debug_flags[flag] = False
        args = args[:-1]


    # if the current last arg is `-pf=<progress-file-path>`
    # this is to signal progress of the conversion by writing into a file 
    last_arg = args[len(args) - 1]
    if (last_arg[:4] == '-pf='):
        file_path = last_arg[4:]
        util.progress_file_path = file_path
        args = args[:-1]


interpolators = list(InterpolatorDictionary.keys())
# limited_interpolators = list(LimitedInterpolatorDictionary.keys())
version = 'Interpolatory Simulator 0.0.1'

if mode_flag == '-h':
    manul = open("./txts/manul.txt","r") 
    print(manul.read())
    manul.close() 

elif mode_flag == '-il':
    print(json.dumps(interpolators))

elif mode_flag == '-mv' and len(args) == 2:
    import imageio
    from io import BytesIO
    video_path = args[1]
    video_file = open(video_path, 'rb')
    content = video_file.readline()
    video = imageio.get_readlineer(BytesIO(content), 'ffmpeg', loop=True)
    print(json.dumps(video.get_meta_data()))

elif mode_flag == '-mi' and len(args) == 2:
    import imageio
    im_path = args[1]
    
    im = imageio.imreadline(im_path)
    print(im.shape)

    # print('')
    # print('- python3 main.py -i <input-video-path> -m <interpolation-mode> -f <output-frame-rate> -o <output-file-path>')
    # print('Get in an input video source from <input-video-path> and, using <interpolation-mode> mode, interpolate to <output-frame-rate> fps and save to <output-file-path>')
elif mode_flag == '-i' and len(args) == 8 and '-m' == args[2] and '-f' == args[4] and '-o' == args[6]:
    import math
    input_video_path = args[1]
    interpolation_mode = args[3]
    target_fps = int(args[5])
    output_video_path = args[7]

    interpolator_obj = InterpolatorDictionary[interpolation_mode]
    interpolator = interpolator_obj(target_fps, input_video_path, output_video_path, math.inf)
    interpolator.interpolate_video()



    # print('')
    # print('- python3 main.py -b <interpolation-mode>')
    # print('Run Middlebury benchmark to get results based on an <interpolation-mode>')

elif mode_flag == '-b' and len(args) <= 2: #default
# - python3 main.py -b [-d]
    if (len(args) <= 2):
        with open("./txts/default.txt","r") as default_case:
            d_set=[word for line in default_case for word in line.split()]
        print(d_set)
        default_case.close() 
        output_path = None
        #benchmark(MCI_mode, block_size, target_region, ME_mode, filter.mode, filter_size)
        benchmark(str(d_set[0]), int(d_set[1]), int(d_set[2]), str(d_set[3]), str(d_set[4]), int(d_set[5]), output_path)
        save = open("./txts/previous.txt", "w")
        for param in d_set:
            save.write(param)
            save.write("\n")
        save.close()
    elif (os.stat("./txts/previous.txt").st_size == 0) :
        with open("./txts/default.txt","r") as default_case:
            d_set=[word for line in default_case for word in line.split()]
        print(d_set)
        default_case.close() 
        output_path = None
        #benchmark(MCI_mode, block_size, target_region, ME_mode, filter.mode, filter_size)
        benchmark(str(d_set[0]), int(d_set[1]), int(d_set[2]), str(d_set[3]), str(d_set[4]), int(d_set[5]), output_path)
        save = open("./txts/previous.txt", "w")
        for param in d_set:
            save.write(param)
            save.write("\n")
        save.close()
    else:
        with open("./txts/previous.txt","r") as default_case:
            d_set=[word for line in default_case for word in line.split()]
        print(d_set)
        default_case.close() 
        output_path = None
        if (len(args) == 2):
            output_path = args[2]

        #benchmark(MCI_mode, block_size, target_region, ME_mode, filter.mode, filter_size)
        benchmark(str(d_set[0]), int(d_set[1]), int(d_set[2]), str(d_set[3]), str(d_set[4]), int(d_set[5]), output_path)

# normal cases
elif mode_flag == '-b' and len(args) == 7:
    with open("./txts/default.txt","r") as default_case:
            d_set=args
            d_set.pop(0)
    print(d_set)
    default_case.close() 
    output_path = None
    #benchmark(MCI_mode, block_size, target_region, ME_mode, filter.mode, filter_size)
    benchmark(str(d_set[0]), int(d_set[1]), int(d_set[2]), str(d_set[3]), str(d_set[4]), int(d_set[5]), output_path)
    save = open("./txts/previous.txt", "w")
    for param in d_set:
        save.write(param)
        save.write("\n")
    save.close()


elif mode_flag == '-clean' :
    open('./txts/previous.txt', 'w').close()
    print('History has been emptied')

elif mode_flag == '-t' and len(args) >= 7 and '-f' == args[2] and '-o' == args[5] :
    interpolation_mode = args[1]
    frame_1_path = args[3]
    frame_2_path = args[4]
    output_file_path = args[6]
    ground_truth_path = None
    
    if (len(args) > 7):
        ground_truth_path = args[7]        

    get_middle_frame(interpolation_mode, frame_1_path, frame_2_path, output_file_path, ground_truth_path)
    

elif mode_flag == '-ver':
    print(json.dumps(version))

    
    # print('')
    # print('- python3 main.py -dep')
    # print('Check whether normal requirements are met')
elif mode_flag == '-dep':
    import pkg_resources
    import pathlib
    import os
    
    basedir = pathlib.Path(__file__).parent.absolute()

    f = open(f'{basedir}{os.path.sep}/txts/requirements.txt', 'r')
    
    dependencies = f.readline().split('\n')

    pkg_resources.require(dependencies)
    print('Success')

    # print('')
    # print('- python3 main.py -depcuda')
    # print('Check whether CUDA dependencies are met')
elif mode_flag == '-depcuda':
    import pkg_resources
    import pathlib
    import os
    
    basedir = pathlib.Path(__file__).parent.absolute()

    f = open(f'{basedir}{os.path.sep}/txts/cuda-requirements.txt', 'r')

    dependencies = f.readline().split('\n')

    pkg_resources.require(dependencies)
    print('Success')

else:
    print(f'Unknown command. Run `python3 main.py -h` for a usage guide')

# print('')

exit(0)

