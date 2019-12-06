def boolean(arg):
    arg = str(arg)

    arg = arg.lower()

    if arg in ("y", "t", "yes", "1", "true"):
        return True
    else:
        return False