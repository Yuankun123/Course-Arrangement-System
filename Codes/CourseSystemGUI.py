import copy
import threading
from tkinter import *
from ttkbootstrap import *
from tkinter import filedialog, messagebox

from Functions import CourseSystem, Group, CompoundGroup
from Translator import TR
colorList = ['sky blue', 'aquamarine', 'light goldenrod', 'bisque', 'rosy brown', 'orange', '#B9CFAD', '#FCAE1E',
             '#59788E']


class CSInfoFrame(LabelFrame):
    infoFrameCollection: list['CSInfoFrame'] = []

    def __init__(self, main_frame, x, y, width, height, cs: CourseSystem | str, **kw):
        self.cs = main_frame.sch.add_cs(cs)

        super(CSInfoFrame, self).__init__(main_frame, **kw)
        self.x, self.y, self.width, self.height = (x, y, width, height)
        self.configure(text=TR.detail_info + self.cs.na)
        self.color_dict: dict[Group | CompoundGroup, str] = {}
        self.color_list = copy.copy(colorList)

        path_label = Label(self, text=TR.course_info_path, style='2.TLabel')
        path_label.place(x=0, y=0, width=390)

        self.path_entry = Entry(self)
        self.path_entry.insert('0', self.cs.info_path)
        self.path_entry.place(x=0, y=20, width=390)

        state_label = Label(self, text='State: ', style='2.TLabel')
        state_label.place(x=0, y=60, width=390)

        self.state_entry = Entry(self)
        self.state_entry.insert('0', self.cs.state)
        self.state_entry.place(x=0, y=80, width=390)

        self.importInfoFile_button = Button(self,
                                            text=TR.import_course_info_file,
                                            command=self.import_info_file)
        self.startArranging_button = Button(self,
                                            text=TR.start_arr,
                                            command=self.generate_arrangement)
        self.display_button = Button(self,
                                     text=TR.display,
                                     command=self.display)
        debug_button = Button(self, text='DEBUG', command=self.debug)
        debug_button.place(relx=0, rely=1, anchor='sw')

        CSInfoFrame.infoFrameCollection.append(self)

    def show(self):
        CSInfoFrame.hide_all()

        self.place(x=self.x, y=self.y, width=self.width, height=self.height)

        self.path_entry.configure(state='normal')
        self.path_entry.delete('0', 'end')
        self.path_entry.insert('0', self.cs.info_path)
        self.path_entry.configure(state='readonly')

        self.state_entry.configure(state='normal')
        self.state_entry.delete('0', 'end')
        self.state_entry.insert('0', self.cs.state)
        self.state_entry.configure(state='readonly')

        self.display_button.place_forget()
        self.importInfoFile_button.place_forget()
        self.startArranging_button.place_forget()
        if self.cs.state == 'Unassigned':
            self.importInfoFile_button.place(relx=1, rely=1, anchor='se')
        elif self.cs.state == 'Info file assigned':
            self.startArranging_button.place(relx=1, rely=1, anchor='se')
        elif self.cs.state == 'Arranging draft completed':
            self.display_button.place(relx=1, rely=1, anchor='se')

    def import_info_file(self):
        input_path = filedialog.askopenfilename(title=TR.choose_file, filetypes=(("csv files", "*.csv"),))
        if input_path != '':
            self.cs.info_path = input_path
            self.cs.read_mo_info()
            self.cs.state = 'Info file assigned'
            self.show()

    def generate_arrangement(self):
        bar_frame = Frame(self)
        bar_frame.place(x=0, y=120, width=390)

        def task_bar():
            pb_hd = Progressbar(bar_frame, orient='horizontal', mode='indeterminate',
                                style='info.Horizontal.TProgressbar')
            pb_hd.pack(anchor='center', fill='both')
            pb_hd.start(20)
            self.master.mainloop()

        def computing_task():
            self.cs.arrange_crs()
            bar_frame.destroy()
            self.master.quit()

        thr = threading.Thread(target=computing_task)
        thr.start()
        task_bar()
        thr.join()

        self.cs.state = 'Arranging draft completed'
        self.show()

    def debug(self):
        print(self)

    @classmethod
    def hide_all(cls):
        for info_frame in cls.infoFrameCollection:
            info_frame.place_forget()

    def display(self):
        # Create new window
        root = Toplevel(background='white')
        root.title(self.cs.na)

        # Create empty text array
        text_array = []
        for j in range(len(self.cs.days) + 1):
            column = []
            for i in range(self.cs.periods_per_day + 1):
                e = Text(root,
                         autostyle=False,
                         wrap='word',
                         fg='black',
                         width=28 if j != 0 else 6,
                         height=8 if i != 0 else 1,
                         font=('Arial', 8)
                         )
                e.grid(row=(i + 1), column=j)
                column.append(e)
            text_array.append(column)

        # display functions for buttons
        def get_color(t: 'CourseTable.Time') -> str:
            if t.pd is None:  # empty time
                return self.color_list[-1]
            else:
                if t.pd.gp in self.color_dict.keys():
                    return self.color_dict[t.pd.gp]
                else:
                    self.color_dict[t.pd.gp] = self.color_list.pop(0)
                    return self.color_dict[t.pd.gp]

        def disable_text_array():
            for column_in in text_array:
                for e_in in column_in:
                    e_in.configure(state='disabled')

        def normalize_text_array():
            for column_in in text_array:
                for e_in in column_in:
                    e_in.configure(state='normal')

        def clear_text_array():
            normalize_text_array()
            for column_in in text_array:
                for e_in in column_in:
                    e_in.delete('1.0', 'end')
            disable_text_array()

        def insert_form():

            normalize_text_array()
            for j_in, column_in in enumerate(text_array):
                for i_in, e_in in enumerate(column_in):

                    if i_in > 0 and j_in > 0:
                        e_in.insert('end', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[(j_in - 1) * self.cs.periods_per_day +
                                                                        (i_in - 1)] + '\n')
                        e_in.tag_add('slot_No', '1.0', '1.1')
                        e_in.tag_configure('slot_No', foreground='red')

                        e_in.configure(bg=get_color(self.cs.courseTable[j_in - 1, i_in - 1]))

                        for lsni, lsn in enumerate(self.cs.courseTable[j_in - 1, i_in - 1].lsns):
                            if lsn.sn.i >= 10:
                                index_for_display = str(lsn.sn.i)
                            else:
                                index_for_display = '0' + str(lsn.sn.i)
                            e_in.insert('end', index_for_display + ' ' + lsn.sn.na + '\n')
                            e_in.tag_add('start', f'{lsni + 2}.0', f'{lsni + 2}.2')
                            e_in.tag_configure('start', foreground='blue')
                    elif i_in == 0:  # week days
                        e_in.insert('end', self.cs.days[j_in - 1])
                    else:  # j_in == 0, time headers
                        e_in.insert('end', self.cs.timeList[j_in - 1])
            disable_text_array()

        def switch_two_slots():
            tg1 = switch_l_entry1.get().upper()
            tg2 = switch_l_entry2.get().upper()
            index1 = 'ABCDEFGHIJKLMNOPQRSTUVWXY'.find(tg1)
            index2 = 'ABCDEFGHIJKLMNOPQRSTUVWXY'.find(tg2)

            self.cs.courseTable.switch_two_time_slots(index1, index2)

            clear_text_array()
            insert_form()

        def switch_two_sessions():
            sni1 = int(switch_n_entry1.get())
            sni2 = int(switch_n_entry2.get())

            if not self.cs.courseTable.switch_two_sns(sni1, sni2):
                messagebox.showwarning(TR.warning, message=TR.cannot_switch)

            clear_text_array()
            insert_form()

        def export_csv():
            saving_path = filedialog.asksaveasfilename(initialfile=TR.export_csv_name + f'{self.cs.na}.csv',
                                                       title=TR.export_as_csv,
                                                       filetypes=(("csv files", "*.csv"),))
            if saving_path:
                self.cs.save_as_csv(saving_path)

        def save_draft():
            saving_path = filedialog.asksaveasfilename(initialfile=TR.save_draft_name + f'{self.cs.na}.txt',
                                                       title=TR.save_as_draft,
                                                       filetypes=(("txt file", "*.txt"),))
            if saving_path:
                try:
                    self.cs.serialize(saving_path)
                except PermissionError:
                    print("The file is being operated by another APP")

        def inspect_conflict():
            conflicts = self.cs.courseTable.inspect()
            if not conflicts:
                message = TR.no_conflict
            else:
                message = ''
                for conflict in conflicts:
                    message += f'{conflict[0]}: {"".join([repr(inst) for inst in conflict[1]])}\n'
            messagebox.showinfo(TR.conflicts, message, parent=root)

        def cross_inspect():
            all_conflicts = self.cs.courseTable.cross_inspect()
            if not all_conflicts:
                message = TR.no_conflict
            else:
                message = ''
                for conflicts_one_cs, cs in all_conflicts:
                    for conflict in conflicts_one_cs:
                        message += f'{conflict[0]}:\n    {", ".join([repr(inst) for inst in conflict[1]])}.\n' \
                                   f'    {TR.conflicts_with} {cs.na}\n'
            messagebox.showinfo(TR.conflicts, message, parent=root)

        def cross_adjust():
            self.cs.courseTable.cross_adjust()
            clear_text_array()
            insert_form()

        # display
        # Insert contents in form to the text array
        insert_form()

        # create Frame for the first button
        upper_frame1 = Frame(root)
        upper_frame1.grid(row=1, column=7, sticky='NWSE', rowspan=2)
        switch_l_entry1 = Entry(upper_frame1, width=12)
        switch_l_entry1.grid(row=0, column=0, sticky='ew')
        switch_l_entry2 = Entry(upper_frame1, width=12)
        switch_l_entry2.grid(row=0, column=1, sticky='ew')
        switch_s_button = Button(upper_frame1, text=TR.switch_two_slots, command=switch_two_slots)
        switch_s_button.grid(row=1, column=0, sticky='ew', columnspan=2)

        # create Frame for the second button
        switch_n_entry1 = Entry(upper_frame1, width=12)
        switch_n_entry1.grid(row=2, column=0, sticky='ew')
        switch_n_entry2 = Entry(upper_frame1, width=12)
        switch_n_entry2.grid(row=2, column=1, sticky='ew')
        switch_c_button = Button(upper_frame1, text=TR.switch_two_sessions, command=switch_two_sessions)
        switch_c_button.grid(row=3, column=0, sticky='ew', columnspan=2)

        # inspect buttons
        inspect_frame = Frame(root)
        inspect_frame.grid(row=3, column=7, sticky='NWSE')
        inspect_button = Button(inspect_frame, text=TR.inspect, command=inspect_conflict)
        inspect_button.pack(fill='both')
        cross_inspect_button = Button(inspect_frame, text=TR.cross_inspect, command=cross_inspect)
        cross_inspect_button.pack(fill='both')
        cross_adjust_button = Button(inspect_frame, text=TR.cross_adjust, command=cross_adjust)
        cross_adjust_button.pack(fill='both')

        # the save draft button
        save_draft_button = Button(root, text=TR.save_as_draft, command=save_draft)
        save_draft_button.grid(row=5, column=7, sticky='WNE')

        #  the export csv button
        save_button = Button(root, text=TR.export_as_csv, command=export_csv)
        save_button.grid(row=6, column=7, sticky='WNE')
