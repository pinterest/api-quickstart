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
        raise ValueError(f'minimum {minimum} > maximum {maximum}')

    # print optional prompt
    if prompt:
        print(prompt) 

    try:
        while True:
            strval = input(f'[{default}] ')
            if strval == '':
                return default
            try:
                intval = int(strval)
            except ValueError:
                print(f'{strval} is not a number')
                continue

            if minimum <= intval and intval <= maximum:
                return intval

            print(f'{strval} is not between {minimum} and {maximum}')
    except KeyboardInterrupt:
        print()
        exit()
