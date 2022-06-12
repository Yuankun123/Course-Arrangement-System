import csv
import pickle
from Functions import CourseSystem, School
colorList = ['sky blue', 'aquamarine', 'light goldenrod', 'bisque', 'rosy brown', 'orange', '#B9CFAD',
             '#59788E', 'brown']


# the following classes add some technical details to the classes they inherit
class GUICourseSystem(CourseSystem):
    def __init__(self, name, sch: 'GUISchool', dayn, pdn_per_day):
        super().__init__(name, sch, dayn, pdn_per_day)
        self.days = sch.days[:dayn]
        self.time_list = sch.timeList[:pdn_per_day]
        self.info_path = 'Unassigned'
        self.state = 'Unassigned'

    @property
    def color_dict(self):
        top_gps = sum([mo.gps for mo in self.top_mos], [])
        return dict(zip(top_gps, colorList[:len(top_gps)]))

    def get_color(self, day, row):
        t = self[day, row]
        if t.pd is None:
            return colorList[-1]
        return self.color_dict[t.pd.gp]

    def save_as_csv(self, saving_path):
        reversed_form = [['Time'] + self.days]
        rows = [[self.time_list[i]] + [''] * self.dayn for i in range(self.pdn_per_day)]
        reversed_form.extend(rows)

        for day in range(self.dayn):
            for row in range(self.pdn_per_day):
                temp = ''
                for lsn in self[day, row].lsns:
                    temp += lsn.sn.na + '\n'
                reversed_form[row + 1][day + 1] = temp

        with open(saving_path, 'w', newline='') as courseArrangement:
            writer = csv.writer(courseArrangement)
            writer.writerows(reversed_form)

    def load_info(self):
        self.read_mo_info(self.info_path)


class GUISchool(School):
    csDict: dict[str, GUICourseSystem]  # type hint

    def __init__(self,
                 name,
                 days=('Mon', 'Tue', 'Wed', 'Thu', 'Fri'),
                 time_list=('08:00 - 09:30', '09:40 - 11:10', '12:30 - 14:00', '14:10 - 15:40', '15:50-16:50')):
        self.days = days
        self.timeList = time_list
        super().__init__(name, len(days), len(time_list))

    def add_cs(self, cs_na: str, dayn, pdn_per_day) -> GUICourseSystem:
        print(self.max_pdn_per_day)
        assert dayn <= self.max_dayn and pdn_per_day <= self.max_pdn_per_day
        if cs_na not in self.csDict.keys():
            self.csDict[cs_na] = GUICourseSystem(cs_na, self, dayn, pdn_per_day)
        return self.csDict[cs_na]

    def serialize(self, saving_path):
        with open(saving_path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def deserialize(cls, open_path) -> 'School':
        with open(open_path, 'rb') as f:
            res = pickle.load(f)
            assert isinstance(res, cls)
            return res


if __name__ == '__main__':
    class _Client:
        Sch = GUISchool('BHSFIC')

        Gr1 = Sch.add_cs('Grade 11', 5, 4)
        Gr1.info_path = 'C:\\Users\\Kunko\\Desktop\\ACAS\\课程信息示例\\courseInfo v2.0.csv'
        Gr1.load_info()
        Gr1.arrange_crs()

        print(Gr1.color_dict)

        '''Gr2 = Sch.add_cs('Grade 12', 5, 4)
        Gr2.info_path = 'C:\\Users\\Kunko\\Desktop\\ACAS\\课程信息示例\\courseInfo v2.0.csv'
        Gr2.load_info()
        Gr2.arrange_crs()

        Gr2.cross_adjust()'''
