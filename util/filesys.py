import glob


def read_all_files(root_dir, file_ext):
    return glob.glob("{}/*.{}".format(root_dir, file_ext))