import os

def make_check_dir(path):
    """
    checks if the directory exists if not creates one

    will return false if the dir doesnt exist and will create it
    true if it does exist

    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)

        return False
    else:
        return True