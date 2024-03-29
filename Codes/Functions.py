"""
Structure:
    Grade:
        Module:
        (1) FEModule: free electives
        (2) REModule: restricted electives
        (3) RModule: required

            .select_num: the number of courses a student need to take from this module. For FE modules,
                this is the maximum number; for RE modules, this would be the exact number; for R modules
                this would be the number of courses of the module

            Group: a set of course sessions of a module from which a student can select one. The number
                of groups of a module is equal to the larger one of the following two numbers:
                1 select_num of the module; 2 the maximum number of sessions led by one same instructor
                Only for FE and RE modules.

                .periods: periods associated with the group

            Course:
            (1) FECourse
            (2) RECourse
            (3) RCourse
                Session:
                    Lesson:

    Instructor
    SClass: A class of students. Only for required courses

    Course Table
    Time
    Period

Contractions:
     na: name
     pd: period
     t: time
     inst: instructor
     fr: frequency

     lsn: lesson
     sn: session
     cr: course
     mo: module
     gr: grade

     shd: shadow
     unavail: unavailable

     cmpd: compound
     -i: index thereof
     -n: number thereof
     -s: plural
"""
import csv
import copy
from Tool import *
from tqdm import tqdm
INDENT = ' '*4


class Instructor:
    def __init__(self, name: str):
        self.na = name
        self.sns: list[Session] = []

    @property
    def ts(self) -> list['CourseSystem.Time']:
        res = []
        for sn in self.sns:
            res.extend(sn.ts)
        return res

    def __repr__(self):
        return f'{self.na}'


class Lesson:
    def __init__(self, session: 'Session', lesson_index):
        self.sn = session
        self.lsni = lesson_index

    @property
    def t(self) -> 'Time | str':
        if type(self.sn.ts) is str:
            return self.sn.ts
        return self.sn.ts[self.lsni]

    def __repr__(self):
        return f'{self.sn.na} L{self.lsni}'


class Session:
    i = 0

    def __init__(self, course: 'Course', session_index: int, instructors: list[Instructor], cs: 'CourseSystem'):
        self.cs = cs
        self.cr = course
        self.sni = session_index
        self.insts = instructors
        self.na = course.naming(session_index)
        self.i = Session.i
        Session.i += 1

        for inst in self.insts:
            inst.sns.append(self)
        self.cs.sns.append(self)

        self.lsns: list[Lesson] = []
        for i in range(self.cr.fr):
            self.lsns.append(Lesson(self, i))

        self._gp: Group | None = None

    @property
    def gp(self):
        return self._gp

    @gp.setter
    def gp(self, gp: 'Group'):
        if self._gp is not None:
            self._gp.sns.remove(self)
        self._gp = gp
        gp.sns.append(self)

    @property
    def ts(self) -> list['CourseSystem.Time'] | str:
        if self.gp is None:
            return 'Group Unarranged'
        if self.gp.pds[0].t is None:
            return 'Time Unarranged'
        return [pd.t for pd in self.gp.pds]

    def __repr__(self):
        return f'{self.na} with {len(self.lsns)} lessons taught by {"".join([inst.na + ", " for inst in self.insts])}'


class Course:
    def __init__(self, name, module: 'Module', instructors: list[Instructor], frequency, cs: 'CourseSystem'):
        self.cs = cs
        self.na = name
        self.mo = module
        self.insts = instructors
        self.fr = frequency

    def naming(self, sni) -> str:
        """return the name of the sni-th session"""
        pass


class ECourse(Course):
    """Elective Courses are available for all students in the student body. Each session has ONLY one
    instructor"""
    def __init__(self, name, module: 'EModule', instructors: list[Instructor], session_indices: list[list],
                 cs: 'CourseSystem'):
        super(ECourse, self).__init__(name, module, instructors, module.fr, cs)
        self.snis = session_indices
        self.sns: list[Session] = []
        for insti, in_snis in enumerate(self.snis):
            for sni in in_snis:
                self.sns.append(Session(self, sni, [instructors[insti]], cs))  # initiate sessions
        self.snn = len(self.sns)

    def naming(self, sni) -> str:
        """return the name of the sni-th session"""
        return f'{self.na} S{sni}'

    def __repr__(self):
        res = f'ECourse {self.na}, {self.snis[-1][-1] + 1} session(s), taught by '\
              f'{"".join([inst.na + ", " for inst in self.insts])}Sessions:\n'
        for sn in self.sns:
            res += f'{INDENT*3}{repr(sn)}\n'
        return res


class RCourse(Course):
    """Required Courses are required for all students in a student body. They have just one session and
    may have several instructors"""
    def __init__(self, name, module: 'RModule', instructors: list[Instructor], frequency, cs: 'CourseSystem'):
        super(RCourse, self).__init__(name, module, instructors, frequency, cs)
        self.sn = Session(self, 0, instructors, cs)

    def naming(self, sni) -> str:
        """return the name of the sni-th session"""
        return f'{self.na}'

    def __repr__(self):
        return f'{INDENT*2}RCourse {self.na}, taught by {"".join([inst.na + ", " for inst in self.insts])}'\
               f'frequency:{self.fr}'


class Module:
    def __init__(self, name, course_cls, cs: 'CourseSystem'):
        self.cs = cs
        self.na = name
        self.Course = course_cls

        # determined after loading courses
        self.crs: list[ECourse | RCourse] = []
        self.gps: list[Group] = []

    @property
    def insts(self) -> list[Instructor]:
        res = sum([cr.insts for cr in self.crs], [])
        return list(set(res))

    @property
    def sns(self) -> list[Session]:
        return sum([cr.sns for cr in self.crs], [])

    def load_crs(self, info_path,  key=TextProcessor.remove_end_blank):
        """
        add all courses of this module to self.crs;
        add instructors to self.gr.insts_dict and self.insts
        """
        pass

    def arrange_gps(self):
        """create group objects for this module"""
        pass

    def arrange_crs(self):
        """bind add sessions to groups"""
        pass


class EModule(Module):
    """All students can select courses from Elective Modules to take. The maximum number of courses
     one can take is select_num. All courses of a same elective module should have same frequencies"""
    def __init__(self, name, frequency, select_num, cs: 'CourseSystem'):
        self.cs = cs
        self.fr = frequency
        self.sln = select_num
        super(EModule, self).__init__(name, ECourse, cs)

    def __repr__(self):
        res = f'EModule {self.na},\n{INDENT}Groups:\n'
        for gp in self.gps:
            res += f'{INDENT*2}{repr(gp)}\n'
        res += f'{INDENT}Courses:\n'
        for cr in self.crs:
            res += f'{INDENT*2}{repr(cr)}\n'
        return res

    @property
    def lei_gpn(self) -> int:
        return self.gpn - self.sln

    @property
    def tot_snn(self) -> int:
        return sum([cr.snn for cr in self.crs])

    @property
    def gpn(self) -> int:
        return len(self.gps)

    def load_crs(self, info_path, key=TextProcessor.remove_end_blank):
        with open(info_path, 'r', encoding="gbk") as f:
            csv_reader = csv.reader(f)
            for line in csv_reader:
                if key(line[0]) == 'Course*' and key(line[2]) == self.na:
                    sn_extractor = 4
                    sn_counter = 0  # session index start from 1
                    snis = []
                    insts = []

                    while sn_extractor < len(line):
                        if line[sn_extractor] != '' and line[sn_extractor - 1] != '':
                            snis.append(list(
                                range(sn_counter, sn_counter + int(line[sn_extractor]))
                            ))
                            sn_counter += int(line[sn_extractor])
                            insts.append(self.cs.sch.add_inst(key(line[sn_extractor - 1])))
                        sn_extractor += 2

                    self.crs.append(
                        self.Course(line[1], self, insts, snis, self.cs)
                    )
        self.crs.sort(key=lambda cr: cr.snn, reverse=True)

    def arrange_gps(self):
        """create group objects for this module"""
        # calculate self.gpn
        minimum = 0  # the minimum number of groups for instructors
        for inst in self.insts:
            # number of sessions the instructor lead
            # in this module
            temp = len([sn for sn in inst.sns if sn.cr in self.crs])
            if temp > minimum:
                minimum = temp
        gpn = max(minimum, self.sln)

        # calculate group capacities
        gp_capas = [self.tot_snn // gpn] * gpn
        for i in range(self.tot_snn % gpn):
            gp_capas[i] += 1

        for i in range(gpn):
            self.gps.append(
                Group(self.fr, self, gp_capas[i], i)
            )

    def arrange_crs_a(self):
        """arrange courses into groups"""

        # LOCAL FUNCTIONS
        def spider_moving(tl, ci, _maxes, bases):
            tl[ci] += 1
            if tl[ci] == _maxes[ci]:  # judge to move another leg
                if -ci == len(tl):
                    pass
                else:
                    spider_moving(tl, ci - 1, _maxes, bases)
                    tl[ci] = copy.copy(bases[ci])
            return tl

        def bi_combination(target_list):
            res = []
            temp = copy.deepcopy(target_list)
            while len(temp) > 1:
                storage = temp.pop(0)
                for bc_index in temp:
                    res.append([storage, bc_index])
            return res

        def list_subtraction(list1, list2):  # assuming that there is no repeated element in each list
            res = []
            for index_s in list1:
                if index_s not in list2:
                    res.append(index_s)
            return res

        def list_comparing(target_list1, target_list2, equ_items: list[list]):
            list1 = target_list1[:]
            list2 = target_list2[:]
            equ_items_local = equ_items[:]
            while 0 < len(list1) and 0 < len(list2):
                if list1[0] == list2[0]:
                    del (list1[0])
                    del (list2[0])
                elif list1[0] < list2[0]:
                    for n_loc, (item1, item2) in enumerate(equ_items_local):
                        if list1[0] == item1:
                            target = item2
                            del (equ_items_local[n_loc])
                            break
                        elif list1[0] == item2:
                            del (equ_items_local[n_loc])
                            target = item1
                            break
                    else:
                        return False

                    for n_loc, item in enumerate(list2):
                        if item == target:
                            del (list2[n_loc])
                            del (list1[0])
                            break
                    else:
                        return False

                else:
                    for n_loc, (item1, item2) in enumerate(equ_items_local):
                        if list2[0] == item1:
                            target = item2
                            del (equ_items_local[n_loc])
                            break
                        elif list2[0] == item2:
                            del (equ_items_local[n_loc])
                            target = item1
                            break
                    else:
                        return False

                    for n_loc, item in enumerate(list1):
                        if item == target:
                            del (list1[n_loc])
                            del (list2[0])
                            break
                    else:
                        return False
            return True

        class CompleteGraph:
            def __init__(self, vertices: list):
                self.vertices = vertices
                self.edges = bi_combination(self.vertices)

            def update_edges(self):
                self.edges = bi_combination(self.vertices)

        # GENERATE ARRANGEMENT FOR ELECTIVES
        circles = [cr.snn for cr in self.crs]
        gp_capas = [gp.capa for gp in self.gps]
        # The Number of groups of time slots that are going to be assigned to multiple course choices
        processing_complete_graph = CompleteGraph([])
        storage_max_graphs = []
        storage_bases_graphs = []
        graphs = []
        circlings = []
        gps_pdis = []

        counter = 0
        for capa in gp_capas:
            storage_bases_graphs.append(counter)
            storage_max_graphs.append(counter + capa)
            gp_pdis = list(range(counter, counter + capa))
            gps_pdis.append(gp_pdis)
            graphs.append(CompleteGraph(
                gp_pdis
            ))
            counter += capa

        arranged_indices = []
        # Arrange elective courses
        for circle in tqdm(circles, desc=f'Arranging Group For {self.na}'):
            assert circle <= 2
            if circle == 2:
                edge_times = {}
                processing_complete_graph.vertices = copy.copy(storage_bases_graphs)
                course_combinations = []

                # boundary for the spider algorithm
                while processing_complete_graph.vertices[0] < storage_max_graphs[0]:
                    processing_complete_graph.update_edges()
                    # to ensure that the processing choice combination is valid
                    # (not containing groups of a same class)
                    if not isoverlapped(processing_complete_graph.edges, circlings):

                        already_counted = False
                        if isoverlapped(processing_complete_graph.vertices, sum(circlings, [])):
                            for i_identifier in course_combinations:
                                if list_comparing(i_identifier, processing_complete_graph.vertices, circlings):
                                    already_counted = True
                                    break

                        if not already_counted:
                            course_combinations.append(copy.copy(processing_complete_graph.vertices))
                            # Accumulation
                            for edge in processing_complete_graph.edges:
                                if not isoverlapped(edge, arranged_indices):
                                    if tuple(edge) in edge_times:
                                        edge_times[tuple(edge)] += 1
                                    else:
                                        edge_times[tuple(edge)] = 0

                                    relative_graphs = []
                                    equivalent_index = 0
                                    for g in graphs:
                                        if isoverlapped(edge, g.vertices):
                                            relative_graphs.append(g)
                                    for e in circlings:
                                        if isoverlapped(e, relative_graphs[0].vertices) \
                                                and isoverlapped(e, relative_graphs[1].vertices):
                                            equivalent_index += 1
                                    for g in list_subtraction(graphs, relative_graphs):
                                        equivalent_index *= len(g.vertices)
                                    edge_times[tuple(edge)] += equivalent_index
                    spider_moving(processing_complete_graph.vertices, -1, storage_max_graphs, storage_bases_graphs)
                # Select group_number to circle
                min_chooser = list(edge_times.items())[0]
                for (key_min_chooser, values_min_chooser) in edge_times.items():
                    if values_min_chooser < min_chooser[1]:
                        min_chooser = [key_min_chooser, values_min_chooser]

                circlings.append(list(min_chooser[0]))
                arranged_indices.extend(list(min_chooser[0]))

        for _ in range(circles.count(1)):  # courses with just one session
            pdi = list_subtraction(list(range(self.tot_snn)), arranged_indices)[0]
            circlings.append([pdi])
            arranged_indices.append(pdi)

        for circling in circlings:
            for i, loc_index in enumerate(circling):
                for gpi, gp_pdis in enumerate(gps_pdis):
                    if loc_index in gp_pdis:
                        circling[i] = gpi

        for cri, circling in enumerate(circlings):
            for sni, gpi in enumerate(circling):
                self.crs[cri].sns[sni].gp = self.gps[gpi]  # group assigned

    def arrange_crs_b(self):
        for sni, sn in enumerate(sum([cr.sns for cr in self.crs], [])):
            sn.gp = self.gps[sni % self.gpn]

    def arrange_crs(self):
        if self.sln > 1:
            for cr in self.crs:
                if cr.snn < self.gpn:
                    self.arrange_crs_a()
                    break
        else:
            self.arrange_crs_b()
        self.auto_adjust()

    def try_regroup(self, re_gpn: int) -> bool:
        if self.gpn < re_gpn < self.tot_snn:
            self.gps.clear()
            gp_capas = [self.tot_snn // re_gpn] * re_gpn
            for i in range(self.tot_snn % re_gpn):
                gp_capas[i] += 1

            for i in range(re_gpn):
                self.gps.append(
                    Group(self.fr, self, gp_capas[i], i)
                )

            self.arrange_crs()
            return True
        return False

    def auto_adjust(self):
        """
        avoid time conflict within groups of this module
        check group by group
        """
        for gp in self.gps:
            for inst in gp.insts:
                while len(gp.sns_of_inst(inst)) > 1:  # teaches more than one session in one group
                    to_be_rearranged = gp.sns_of_inst(inst)[-1]

                    # check available groups:
                    available_gps = []
                    for check_gp in self.gps:
                        if inst not in check_gp.insts:
                            available_gps.append(check_gp)
                            break

                    # all sessions in available groups
                    target_session = None
                    for sn in sum([available_gp.sns for available_gp in available_gps], []):
                        if inst not in sn.insts and not isoverlapped(sn.insts, gp.insts):
                            target_session = sn
                    print('auto adjusting')
                    self.switch_two_sns(to_be_rearranged, target_session)

    @staticmethod
    def switch_two_sns(sn1, sn2):
        temp_gp = sn1.gp
        sn1.gp = sn2.gp
        sn2.gp = temp_gp


class RModule(Module):
    def __init__(self, cs: 'CourseSystem'):
        super(RModule, self).__init__('R', RCourse, cs)

    def __repr__(self):
        res = f'RModule: \n'
        for cr in self.crs:
            res += repr(cr) + '\n'
        return res

    def load_crs(self, info_path, key=TextProcessor.remove_end_blank):
        with open(info_path, 'r', encoding="gbk") as f:
            csv_reader = csv.reader(f)
            for line in csv_reader:
                if key(line[0]) == 'RCourse*':
                    insts = [self.cs.sch.add_inst(key(inst_na)) for inst_na in line[3:] if inst_na != '']
                    self.crs.append(
                        self.Course(line[1], self, insts, int(line[2]), self.cs)
                    )

    def arrange_gps(self):
        for i, cr in enumerate(self.crs):
            self.gps.append(Group(cr.fr, self, 1, i))

    def arrange_crs(self):
        for cri, cr in enumerate(self.crs):
            cr.sn.gp = self.gps[cri]


class Period:
    def __init__(self, group: 'Group', pdi: int):
        self.gp = group
        self.pdi = pdi
        self._t: CourseSystem.Time | None = None
        self.master: CompoundPeriod | None = None

    @property
    def t(self):
        if self.master is None:
            return self._t
        return self.master.t

    @t.setter
    def t(self, new_t: 'CourseSystem.Time'):
        if self.master is None:
            self._t = new_t
            if new_t is not None:
                new_t.pd = self
        else:
            assert False

    @property
    def lsns(self) -> list[Lesson]:
        """return a lesson list"""
        return [sn.lsns[self.pdi] for sn in self.gp.sns]

    def __repr__(self):
        res = f'P{self.pdi} on {self.t}. Lessons:\n'
        for lsn in self.lsns:
            res += f'{INDENT*3}{repr(lsn.sn)}\n'
        return res


class Group:
    def __init__(self, span: int, module: Module, capacity: int, gpi):
        self.gpi = gpi
        self.span = span
        self.mo = module
        self.capa = capacity
        self.pds = [Period(self, i) for i in range(span)]

        self.sns: list[Session] = []
        self.master: CompoundGroup | None = None  # may be mastered by a compound group

    @property
    def ts(self) -> list['CourseSystem.Time']:
        res = [pd.t for pd in self.pds]
        return res

    @ts.setter
    def ts(self, new_ts):
        if self.master is None:
            for pdi, pd in enumerate(self.pds):
                pd.t = new_ts[pdi]
        else:
            assert False

    def sns_of_inst(self, inst: Instructor) -> list[Session]:
        return [sn for sn in self.sns if inst in sn.insts]

    @property
    def insts(self):
        res = sum([sn.insts for sn in self.sns], [])
        return res

    def __repr__(self):
        res = f'Group #{self.gpi} of {self.mo.na}'
        return res


class CompoundPeriod:
    def __init__(self, parent_pd: Period, group: 'CompoundGroup', pdi: int):
        self.gp = group
        self.pdi = pdi

        self.subpds: list[Period] = []
        self._t: CourseSystem.Time | None = None

        self.slave_subpd(parent_pd)

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, new_t: 'CourseSystem.Time'):
        self._t = new_t
        new_t.pd = self

    @property
    def lsns(self) -> list[Lesson]:
        return sum([pd.lsns for pd in self.subpds], [])

    def slave_subpd(self, new_subpd: Period):
        self.subpds.append(new_subpd)
        new_subpd.master = self

    def __repr__(self):
        res = f'P{self.pdi} on {self.t}. Lessons:\n'
        for lsn in self.lsns:
            res += f'{INDENT*3}{repr(lsn.sn)}\n'
        return res


class CompoundGroup:
    def __init__(self, parent_gp: Group, cmpd_module: 'CompoundModule'):
        self.span = parent_gp.span
        self.cmpd_mo = cmpd_module

        self._cmpd_pds = [CompoundPeriod(parent_gp.pds[i], self, i) for i in range(self.span)]
        self.subgps: list[Group] = [parent_gp]
        parent_gp.master = self

        self.new_subgps: list[Group] = []

    @property
    def cmpd_pds(self):
        return sorted(self._cmpd_pds, key=lambda x: len(x.lsns))

    @property
    def remained_pdn(self):
        return self.span - sum([subgp.span for subgp in self.new_subgps])

    @property
    def sns_sum(self):
        return sum([len(subgp.sns) for subgp in (self.subgps + self.new_subgps)])

    @property
    def ts(self) -> list['CourseSystem.Time']:
        res = [cmpd_pd.t for cmpd_pd in self.cmpd_pds]
        assert len(res) == len(set(res))
        return res

    @ts.setter
    def ts(self, new_ts):
        for cmpd_pdi, cmpd_pd in enumerate(self.cmpd_pds):
            cmpd_pd.t = new_ts[cmpd_pdi]

    def slave_gp(self, new_subgp):
        self.subgps.append(new_subgp)
        new_subgp.master = self
        for cmpd_pdi, cmpd_pd in enumerate(self.cmpd_pds[:new_subgp.span]):  # order matters
            cmpd_pd.slave_subpd(new_subgp.pds[cmpd_pdi])

    def try_add_group(self, new_subgp: 'Group'):
        if new_subgp.span > self.remained_pdn:
            return False
        for subgp in self.subgps:
            if isoverlapped(subgp.insts, new_subgp.insts):
                return False
        else:
            self.new_subgps.append(new_subgp)
            return True

    def confirm(self):
        for new_subgp in self.new_subgps:
            self.slave_gp(new_subgp)
        self.new_subgps.clear()

    def cancel(self):
        self.new_subgps.clear()

    def __repr__(self):
        res = f'A Compound Group with {len(self.subgps)} subgroups. On {self.ts}. Sessions:\n'
        for gp in self.subgps:
            for sn in gp.sns:
                res += f'{INDENT * 3}{sn.na}\n'
        return res


class CompoundModule:
    """to overlap several modules in a course table"""
    def __init__(self, parent: EModule):
        print('Parent:', parent)
        self.cmpd_gpn = parent.gpn
        self.fr = parent.fr
        self.ini_lei_gpn = parent.lei_gpn
        self._cmpd_gps = [CompoundGroup(parent.gps[i], self) for i in range(self.cmpd_gpn)]
        self.submos: list[EModule] = [parent]

    @property
    def lei_pdn(self):
        return self.ini_lei_gpn * self.fr - sum([mo.fr for mo in self.submos[1:]])

    @property
    def gps(self) -> list[CompoundGroup]:
        # the compound group with the smallest number of sessions comes first
        return sorted(self._cmpd_gps, key=lambda x: x.sns_sum)

    def try_add_module(self, new_submo: EModule) -> bool:
        # submodules cannot coexist without some groups overlap to the same compound group
        if new_submo.fr > self.lei_pdn:
            return False

        for submo in self.submos:
            if new_submo.gpn < submo.gpn:
                # regroup
                if new_submo.try_regroup(submo.gpn):
                    pass
                else:
                    return False
            if submo.fr // new_submo.fr * submo.gpn < new_submo.gpn:
                return False
        print('regrouped', [gp.sns for gp in new_submo.gps])

        used_cmpd_gp = set([])
        gps_copy = sorted(new_submo.gps, key=lambda x: x.capa, reverse=True)  # larger group first
        for i in range(new_submo.gpn):
            for cmpd_gp in self.gps:  # order matters
                if cmpd_gp.try_add_group(gps_copy[i]):  # successfully add group
                    used_cmpd_gp.add(cmpd_gp)
                    break
            else:
                for cmpd_gp in self.gps:
                    cmpd_gp.cancel()
                return False

        if len(used_cmpd_gp) < self.cmpd_gpn:  # haven't fill
            for cmpd_gp in self.gps:
                cmpd_gp.cancel()
            return False

        for cmpd_gp in self.gps:
            cmpd_gp.confirm()
        self.submos.append(new_submo)
        return True


class Shadow(TimeTable):
    """to specify the unavailable instructors on each time."""
    class Time(TimeTable.Time):
        i = 0

        def __init__(self, table: 'Shadow'):
            super(Shadow.Time, self).__init__(table)
            self.insts: list[Instructor] = []

    def __init__(self, width, height, unavail_dict: dict[Instructor, list[tuple[int, int]]] = None):
        super(Shadow, self).__init__(width, height)
        if unavail_dict is not None:
            for inst, unavail_ts in unavail_dict.items():
                for day, row in unavail_ts:
                    self[day, row].insts.append(inst)

    def merge(self, another_shadow: 'Shadow'):
        for day in range(self.height):
            for row in range(self.width):
                if another_shadow[day, row] is not None:
                    self[day, row].insts.extend(another_shadow[day, row].insts)
                    self[day, row].insts = list(set(self[day, row].insts))

    def inspect(self) -> list[tuple['CourseSystem.Time', list[Instructor]]]:
        """inspect internal conflicts"""
        res = []
        for t in self:
            if find_repeat_items(t.insts):
                res.append((t, find_repeat_items(t.insts)))
        return res

    def _shadow_inspect(self, shd: 'Shadow') -> list[tuple['CourseSystem.Time', list[Instructor]]]:
        """inspect conflicts with a shadow"""
        res = []
        for day in range(self.width):
            for row in range(self.height):
                conflicts = find_repeat_items(list(set(self[day, row].insts)) + list(set(shd[day, row].insts)))
                if conflicts:
                    res.append((self[day, row], conflicts))
        return res

    def display(self):
        res = ''
        for day in range(self.width):
            for row in range(self.height):
                res += f'{day}, {row}, {self[day, row].insts}\n'
        return res


class CourseSystem(Shadow):
    class Time(TimeTable.Time):
        """
        Each instance of this kind of 'Time':
        Directly stores the reference of the period (may be compound) bound to it.
        Has an immutable property that indicates the instructors having class on this time.
        """
        i = 0

        def __init__(self, table: 'CourseSystem'):
            assert isinstance(table, CourseSystem)
            super(CourseSystem.Time, self).__init__(table)
            self.pd: Period | CompoundPeriod | None = None

        @property
        def insts(self):
            return sum([lsn.sn.insts for lsn in self.lsns], [])

        @property
        def lsns(self) -> list[Lesson]:
            if self.pd is None:
                return []
            return self.pd.lsns

        def display(self) -> str:
            if self.pd is None:
                return f'T{self.vtc_i}, Day{self.day} P #{self.row}. Empty'
            res = f'T{self.vtc_i}, Day{self.day} P #{self.row}. Lessons:\n'
            for lsn in self.lsns:
                res += f'{INDENT * 3}{repr(lsn.sn)}\n'
            return res

        def __repr__(self):
            return f'Day{self.day} T#{self.row}'

    def __init__(self, name, sch: 'School', dayn, pdn_per_day):
        self.pdn_per_day = pdn_per_day
        self.dayn = dayn
        super(CourseSystem, self).__init__(self.dayn, self.pdn_per_day)

        self.na = name
        self.sch = sch

        self.mos: list[Module] = []  # a list of all simple modules, elective or required
        self.top_mos: list[CompoundModule | EModule] = []
        self.sns: list[Session] = []  # for session searching

        self.avail_t: list[CourseSystem.Time] = []
        for i in range(self.pdn_per_day * self.dayn):
            reversed_i = i % self.dayn * self.pdn_per_day + i // self.dayn
            self.avail_t.append(self[reversed_i])

    def read_mo_info(self, info_path, key=TextProcessor.remove_end_blank):
        """read module info from self.path. The construction of modules involve reading course info
        from the same file. So, after this function is executed, the structure constituted by CourseSystem,
        Modules, Courses, Sessions, Lessons and Instructors is constructed"""

        Session.i = 0  # reset session indexing
        with open(info_path, 'r', encoding="gbk") as f:
            csv_reader = csv.reader(f)
            for line in csv_reader:
                if line[0] == '/*':
                    continue
                elif line[0] == 'Module*':
                    self.mos.append(EModule(name=key(line[1]),
                                            select_num=int(line[2]),
                                            frequency=int(line[3]),
                                            cs=self))
                    self.mos[-1].load_crs(info_path)
                    self.mos[-1].arrange_gps()

        self.mos.append(RModule(self))
        self.mos[-1].load_crs(info_path)
        self.mos[-1].arrange_gps()

    def arrange_crs(self):
        for mo in self.mos:
            mo.arrange_crs()
        self.load_e_modules()
        self.load_r_module()

    def _add_time_for_module(self, mo: CompoundModule | Module):
        for gp in mo.gps:
            gp.ts = [self.avail_t.pop(0) for _ in range(gp.span)]
        self.top_mos.append(mo)

    def load_e_modules(self):
        emos = [mo for mo in self.mos if isinstance(mo, EModule)]

        loose_emo_stack = []
        for emo in emos:
            if emo.lei_gpn == 0:  # compact situation
                self._add_time_for_module(emo)
            else:  # loose situation
                loose_emo_stack.append(emo)
        if len(loose_emo_stack) == 0:
            return

        cmpd_emos = []
        loose_emo_stack.sort(key=lambda x: x.fr, reverse=True)
        print('fr sorted (reversed)', loose_emo_stack)
        while len(loose_emo_stack) > 0:
            parent = loose_emo_stack.pop(0)  # parent is the module with the largest fr
            cmpd_emo = CompoundModule(parent)  # create compound module
            cmpd_emos.append(cmpd_emo)

            loose_emo_stack.sort(key=lambda x: x.gpn)  # modules with more groups take higher priority
            print('gpn sorted', loose_emo_stack)
            moi = len(loose_emo_stack) - 1
            while moi >= 0:
                if cmpd_emo.try_add_module(loose_emo_stack[moi]):
                    loose_emo_stack.pop(moi)
                moi -= 1
            loose_emo_stack.sort(key=lambda x: x.fr, reverse=True)

        for cmpd_emo in cmpd_emos:
            self._add_time_for_module(cmpd_emo)

    def load_r_module(self):
        for mo in self.mos:
            if isinstance(mo, RModule):
                self._add_time_for_module(mo)

    def switch_two_sns(self, sni1, sni2):
        sn1 = self.sns[sni1]
        sn2 = self.sns[sni2]
        if sn1.cr.mo == sn2.cr.mo:
            EModule.switch_two_sns(sn1, sn2)
            return True
        return False

    def switch_two_time_slots(self, ti1=-1, ti2=-1):
        _t1 = self[ti1]
        _t2 = self[ti2]

        temp_pd = _t2.pd
        if _t1.pd is not None:
            _t1.pd.t = _t2  # associate t2 to pd1
        else:
            _t2.pd = None  # associate t2 to None
        if temp_pd is not None:
            temp_pd.t = _t1  # associate t1 to pd2
        else:
            _t1.pd = None  # associate t1 to None

    def cross_inspect(self) -> list[tuple[list[tuple['CourseSystem.Time', list[Instructor]]], 'CourseSystem']]:
        course_systems = self.sch.get_other_cs(self)
        res = []
        assert self not in course_systems
        for cs in course_systems:
            temp = self._shadow_inspect(cs)
            if temp:
                res.append((temp, cs))
        return res

    def _shadow_adjust(self, shd: 'Shadow'):
        """
        This function rearranges time slots to avoid conflicts with a given shadow.
        The easiest way to achieve this is by switching time slots holding periods of
        different groups. Since the modules (and thus the groups) are assigned to time slots horizontally,
        in this function we switch time slots vertically.
        """
        for i, t in enumerate(self):
            temp = 1
            while isoverlapped(t.insts, shd[t.day, t.row].insts):
                self.switch_two_time_slots(i, i + temp)
                temp += 1

    def cross_adjust(self):
        """adjust according to other cs and the shadow of the school"""
        merged_shadow = self.sch.shadow
        for cs in self.sch.get_other_cs(self):
            merged_shadow.merge(cs)
        self._shadow_adjust(merged_shadow)

    def __repr__(self):
        res = ''
        for mo in self.mos:
            res += repr(mo) + '\n'
        return res + f'\n{"="*100}'*2


class School:
    def __init__(self, name, max_dayn, max_pdn_per_day):
        self.na = name
        self.max_dayn = max_dayn
        self.max_pdn_per_day = max_pdn_per_day
        self.instDict: dict[str, Instructor] = {}
        self.csDict: dict[str, CourseSystem] = {}
        self.shadow = Shadow(max_dayn, max_pdn_per_day)

    def add_inst(self, name) -> Instructor:
        if name not in self.instDict.keys():
            self.instDict[name] = Instructor(name)
        return self.instDict[name]

    def add_cs(self, cs_na: str, dayn, pdn_per_day) -> CourseSystem:
        assert dayn <= self.max_dayn and pdn_per_day <= self.max_pdn_per_day
        if cs_na not in self.csDict.keys():
            self.csDict[cs_na] = CourseSystem(cs_na, self, dayn, pdn_per_day)
        return self.csDict[cs_na]

    def get_other_cs(self, cntr_cs: CourseSystem) -> list[CourseSystem]:
        res = []
        for cs in self.csDict.values():
            if cs is not cntr_cs:
                res.append(cs)
        return res


if __name__ == '__main__':
    class _Client:
        Sch = School('BHSFIC', 5, 5)

        Gr1 = Sch.add_cs('Grade 11', 5, 5)
        info_path = 'C:\\Users\\Kunko\\Desktop\\12th(1).csv'
        Gr1.read_mo_info(info_path)
        Gr1.arrange_crs()

