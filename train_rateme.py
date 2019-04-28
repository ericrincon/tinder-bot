import argparse

from bernard.vision.data import RateMeDataset, list_dir


def args_str(arg: str):
    if arg in ("", "none", "n"):
        return None

    return arg.strip().lower()


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--dir-path", type=args_str, default="")
    args = arg_parser.parse_args()

    file_paths = None

    train_dataset = RateMeDataset(
        dir_path=args.dir_path,
        file_paths=file_paths
    )


    print(len(train_dataset))

if __name__ == '__main__':
    main()
