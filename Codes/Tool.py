class TextProcessor:
    @staticmethod
    def remove_end_blank(string: str):
        while string and string[-1] == ' ':
            string = string[:-1]
        return string


def find_repeat_items(input_list: list) -> list:
    res = []
    for n1, item1 in enumerate(input_list):
        for n2, item2 in enumerate(input_list[n1 + 1:]):
            if item1 == item2 and item1 not in res:
                res.append(item1)
    return res


def isoverlapped(list1, list2) -> bool:
    for i1 in list1:
        for i2 in list2:
            if i1 == i2:
                return True

    return False
