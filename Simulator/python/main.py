import sys
import json
import os

sys.path.append('./src')
from src import util, Interpolator, Benchmark, Globals
<<<<<<< HEAD
from src.Interpolator import InterpolatorDictionary
from src.Benchmark import benchmark, benchmarkCNN, get_middle_frame
=======
from src.Interpolator import InterpolatorDictionary, InterpolatorDocs
from src.Benchmark import benchmark, get_middle_frame
>>>>>>> master

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
<<<<<<< HEAD
    manual = open("./txts/manual.txt","r") 
    print(manual.read())
    manual.close() 
=======
    print('======')
    print('Manual')
    print('======')

    print('')
    print('- python3 main.py -h')
    print('Get this help.')

    print('')
    print('- python3 main.py -il')
    print('List all supported interpolation modes')

    print('')
    print('- python3 main.py -doc')
    print('List all supported interpolation modes and their CLI usage guide')

    print('')
    print('- python3 main.py -mv <video-path>')
    print('Load a video and print metadata to stdout. If not supported, will return non-zero value')
    
    print('')
    print('- python3 main.py -mi <video-path>')
    print('Load an image and print height, width, and colour dimensions to stdout. If not supported, will return non-zero value')
    
    print('')
    print('- python3 main.py -i <input-video-path> -m <interpolation-mode>[:<settings>] -f <output-frame-rate> -o <output-file-path>')
    print('Get in an input video source from <input-video-path> and, using <interpolation-mode> mode, interpolate to <output-frame-rate> fps and save to <output-file-path>')
    print('Extra configuration settings can be set in <settings> using semicolon separated key-value pairs, e.g. for MEMCI, "block_size=32;filter_size=8;"')
    print('See interpolation mode usage guides in `python3 main.py -doc`')

    print('')
    print('- python3 main.py -b <interpolation-mode>[:<settings>] [<output-folder>]')
    print('Run Middlebury benchmark to get results based on an <interpolation-mode>')
    print('If provided, outputs interpolated images to <output-folder>')
    print('Extra configuration settings can be set in <settings> using semicolon separated key-value pairs, e.g. for MEMCI, "block_size=32;filter_size=8;"')
    print('See interpolation mode usage guides in `python3 main.py -doc`')
    
    print('')
    print('- python3 main.py -t <interpolation-mode>[:<settings>] -f <frame1> <frame2> -o <output-file-path> [<ground-truth-path>]')
    print('Using <interpolation mode, get the interpolated midpoint frame between <frame1> and <frame2>, saving the output to <output-file-path>')
    print('Extra configuration settings can be set in <settings> using semicolon separated key-value pairs, e.g. for MEMCI, "block_size=32;filter_size=8;"')
    print('See interpolation mode usage guides in `python3 main.py -doc`')
    print('If [<ground-truth-path>] provided, metrics (PSNR & SSIM) are returned')
    
    
    print('')
    print('- python3 main.py -ver')
    print('Get version')

    print('')
    print('- python3 main.py -dep')
    print('Check whether normal requirements are met')

    print('')
    print('- python3 main.py -depcuda')
    print('Check whether CUDA dependencies are met')

>>>>>>> master

elif mode_flag == '-il':
    print(json.dumps(interpolators))

    
    # print('')
    # print('- python3 main.py -doc')
    # print('List all supported interpolation modes and their CLI usage guide')
elif mode_flag == '-doc':
    print('TODO')

# this schema is for gui
elif mode_flag == '-schema':
    print(json.dumps(InterpolatorDocs))


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
    
<<<<<<< HEAD
    im = imageio.imreadline(im_path)
    print(im.shape)
=======
    im = imageio.imread(im_path)
>>>>>>> master

    # print('')
    # print('- python3 main.py -i <input-video-path> -m <interpolation-mode>[:<settings>] -f <output-frame-rate> -o <output-file-path>')
elif mode_flag == '-i' and len(args) == 8 and '-m' == args[2] and '-f' == args[4] and '-o' == args[6]:
    import math
    input_video_path = args[1]
    interpolation_mode, settings = util.deconstruct_interpolation_mode_and_settings(args[3])

    target_fps = int(args[5])
    output_video_path = args[7]

    interpolator_obj = InterpolatorDictionary[interpolation_mode]
    interpolator = interpolator_obj(target_fps, input_video_path, output_video_path, math.inf, **settings)
    interpolator.interpolate_video()



<<<<<<< HEAD
    # print('')
    # print('- python3 main.py -b <interpolation-mode>')
    # print('Run Middlebury benchmark to get results based on an <interpolation-mode>')

elif mode_flag == '-b' and len(args) <= 2: #default
# - python3 main.py -b [-d]/[MCI]
    if (len(args) == 2):
        if args[1] == '-d' :
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
            interpolation_mode = args[1]
            output_path = None
            benchmarkCNN(interpolation_mode, output_path)
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
    # with open("./txts/default.txt","r") as default_case:
    d_set=args
    d_set.pop(0)
    print(d_set)
    # default_case.close()
    output_path = None
    #benchmark(MCI_mode, block_size, target_region, ME_mode, filter.mode, filter_size)
    benchmark(str(d_set[0]), int(d_set[1]), int(d_set[2]), str(d_set[3]), str(d_set[4]), int(d_set[5]), output_path)
    save = open("./txts/previous.txt", "w")
    for param in d_set:
        save.write(param)
        save.write("\n")
    save.close()

#change individual arg
elif mode_flag == '-c' and 2 <= len(args) <7:
    print("change mode")

    with open("./txts/default.txt", "r") as default_case:
        d_set = [word for line in default_case for word in line.split()]
    # print(d_set)
    default_case.close()

    d_change = args
    d_change.pop(0)
    for i in range (len(d_change)):
        cur=str(d_change[i])
        index=int(cur[0])
        print(cur,index)
        if index==0 or index==3 or index==4:
            d_set[index]=cur[2:]
        else:
            d_set[index]=int(cur[2:])
    print(d_set)
    output_path = f"./middleBlurry_output./{d_set[0]}_{d_set[1]}_{d_set[2]}_{d_set[3]}_{d_set[4]}_{d_set[5]}"
    try :
        os.makedirs(output_path)
    except OSError:
        print("File to create directory %s" %output_path)
    else:
        print("Successfully created the directory %s" % output_path)


    # benchmark(MCI_mode, block_size, target_region, ME_mode, filter.mode, filter_size)
    benchmark(str(d_set[0]), int(d_set[1]), int(d_set[2]), str(d_set[3]), str(d_set[4]), int(d_set[5]), output_path)
    save = open("./txts/previous.txt", "w")
    for param in d_set:
        save.write(str(param))
        save.write("\n")
    save.close()

elif mode_flag == '-clean' :
    open('./txts/previous.txt', 'w').close()
    print('History has been emptied')

=======
elif mode_flag == '-b' and len(args) >= 2:
    interpolation_mode, settings = util.deconstruct_interpolation_mode_and_settings(args[1])

    output_path = None
    if (len(args) > 2):
        output_path = args[2]

    interpolator_obj = InterpolatorDictionary[interpolation_mode]
    interpolator = interpolator_obj(2, **settings)
    benchmark(interpolator, output_path)
    

>>>>>>> master
elif mode_flag == '-t' and len(args) >= 7 and '-f' == args[2] and '-o' == args[5] :

    interpolation_mode, settings = util.deconstruct_interpolation_mode_and_settings(args[1])

    frame_1_path = args[3]
    frame_2_path = args[4]
    output_file_path = args[6]
    ground_truth_path = None
    
    if (len(args) > 7):
        ground_truth_path = args[7]        

    interpolator_obj = InterpolatorDictionary[interpolation_mode]
    interpolator = interpolator_obj(2, **settings)
    get_middle_frame(interpolator, frame_1_path, frame_2_path, output_file_path, ground_truth_path)
    

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

