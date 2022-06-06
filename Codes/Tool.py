class TimeTable:
    _all_t: tuple

    class Time:
        i = 0

        def __init__(self, table):
            self.tb = table
            self.vtc_i = table.Time.i  # counted vertically
            self.day = self.vtc_i // self.tb.height  # day start from 0
            self.row = self.vtc_i % self.tb.height  # row start from 0
            self.hrz_i = self.row * self.tb.width + self.day
            table.Time.i += 1

    def __init__(self, width, height):
        self.Time.i = 0
        self.width = width
        self.height = height
        self._all_t = tuple([self.Time(self) for _ in range(self.width * self.height)])

    def __getitem__(self, item: tuple | int):
        if type(item) is tuple:
            day, row = item
            for t in self:
                if t.day == day and t.row == row:
                    return t
        if type(item) is int:
            for t in self:
                if t.vtc_i == item:
                    return t

    def __len__(self):
        return len(self._all_t)

    def __iter__(self):
        return self._all_t.__iter__()

    def min_size(self, other: 'TimeTable') -> tuple[int, int]:
        width = min(self.width, other.width)
        height = min(self.height, other.height)
        return width, height


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
