def __find_middle(input_list):
    middle = float(len(input_list)) / 2
    if middle % 2 != 0:
        return int(middle - .5)
    else:
        return int(middle)


def __convert(s):
    # initialization of string to ""
    new = ""

    # traverse in the string
    for x in s:
        new += x

        # return string
    return new


def __find_number(value_char_list):
    number_char_list = []
    for char in value_char_list:
        if char.isnumeric():
            number_char_list.append(char)
    return number_char_list


def __mask_center(value_char_list, __center):
    number_char_list = __find_number(value_char_list)
    middle = int(__find_middle(number_char_list))
    mask_result_list = []
    number_index = 0
    for index, char in enumerate(value_char_list):
        if char.isnumeric():
            if __center(number_index, middle):
                mask_result_list.append("*")
            else:
                mask_result_list.append(char)
            number_index = number_index + 1
        else:
            mask_result_list.append(char)
    return __convert(mask_result_list)


def __mask_last(value_char_list, __last):
    number_char_list = __find_number(value_char_list)
    last = len(number_char_list)
    mask_result_list = []
    number_index = 0
    for index, char in enumerate(value_char_list):
        if char.isnumeric():
            if __last(number_index, last):
                mask_result_list.append("*")
            else:
                mask_result_list.append(char)
            number_index = number_index + 1
        else:
            mask_result_list.append(char)
    return __convert(mask_result_list)


def __split(value_):
    return [char for char in value_]


def __center_3(number_index, middle):
    return middle - 1 <= number_index <= middle + 1


def __center_5(number_index, middle):
    return middle - 2 <= number_index <= middle + 2


def __last_3(number_index, last_index):
    return last_index - 3 <= number_index < last_index


def __last_6(number_index, last_index):
    return last_index - 6 <= number_index < last_index


def encrypt_center_3(value_, params=None):
    value_char_list = __split(value_)
    return __mask_center(value_char_list, __center_3)


def encrypt_center_5(value_, params=None):
    value_char_list = __split(value_)
    return __mask_center(value_char_list, __center_5)


def encrypt_last_3(value_, params=None):
    value_char_list = __split(value_)
    return __mask_last(value_char_list, __last_3)


def encrypt_last_6(value_, params=None):
    value_char_list = __split(value_)
    return __mask_last(value_char_list, __last_6)
