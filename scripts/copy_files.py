import argparse
import os

from shutil import copyfile

included_extensions = ['jpg', 'jpeg', 'bmp', 'png', 'gif']


def list_dirs(dir_path: str):
    return [f.path for f in os.scandir(dir_path) if f.is_dir()]


def list_jpg(dir_path: str):
    return [fn for fn in os.listdir(dir_path) \
            if any(fn.endswith(ext) for ext in included_extensions)]


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--dir")
    arg_parser.add_argument("--output-dir")
    args = arg_parser.parse_args()

    dirs = list_dirs(args.dir)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for image_dir in dirs:
        image_paths = list_jpg(image_dir)
        dir_image_path = image_dir.split("/")[-1]

        if len(image_paths) > 0:

            for image_path in image_paths:
                dst = os.path.join(args.output_dir, "{}_{}".format(dir_image_path, image_path))
                src = os.path.join(image_dir, image_path)

                copyfile(src, dst)


if __name__ == '__main__':
    main()
