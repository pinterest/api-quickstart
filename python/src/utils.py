import os


def input_number(prompt, minimum, maximum, default=None):
    """
    Prompt for a numerical input between minimum and maximum.
    If the default is not specified, the default is the minimum.
    """
    if not default:
        default = minimum
    if minimum == maximum:
        return minimum
    if minimum > maximum:
        raise ValueError(f"minimum {minimum} > maximum {maximum}")

    # print optional prompt
    if prompt:
        print(prompt)

    try:
        while True:
            strval = input(f"[{default}] ")
            if strval == "":
                return default
            try:
                intval = int(strval)
            except ValueError:
                print(f"{strval} is not an integer")
                continue

            if minimum <= intval and intval <= maximum:
                return intval

            print(f"{strval} is not between {minimum} and {maximum}")
    except KeyboardInterrupt:
        print()
        exit()


def input_one_of(prompt, one_of_list, default):
    if prompt:
        print(prompt)

    one_of_list_casefolded = list(map(str.casefold, one_of_list))

    try:
        while True:
            value = str.casefold(input(f"[{default}] "))
            if value == "":
                return default
            for idx, item in enumerate(one_of_list_casefolded):
                if value == item:
                    return one_of_list[idx]
            print(f"input must be one of {one_of_list}")
    except KeyboardInterrupt:
        print()
        exit()


def input_path_for_write(prompt, default):
    if prompt:
        print(prompt)

    try:
        while True:
            path = input(f"[{default}] ")
            if path == "":
                path = default
            if os.path.exists(path) and "yes" != input_one_of(
                "Overwrite this file?", ["yes", "no"], "no"
            ):
                continue
            try:  # check whether the file can be created
                open(path, "w").close()
                return path
            except OSError:
                print("Error: can not write to this file.")
    except KeyboardInterrupt:
        print()
        exit()
