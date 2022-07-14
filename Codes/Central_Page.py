import threading
from tkinter import *
from ttkbootstrap import *
from tkinter import filedialog, simpledialog, messagebox

from Translator import TR
from GUIPreparation import GUICourseSystem, GUISchool


class CSInfoFrame(LabelFrame):
    cs: GUICourseSystem

    def __init__(self, main_frame: 'CentralPage', x, y, width, height, cs: GUICourseSystem, **kw):
        self.button_frame = None
        self.cs = cs

        super(CSInfoFrame, self).__init__(main_frame, **kw)
        self.x, self.y, self.width, self.height = (x, y, width, height)
        self.configure(text=TR.detail_info + self.cs.na)

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
            self.cs.load_info()
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

    @classmethod
    def hide_all(cls):
        for info_frame in page.csInfoFrames.values():
            info_frame.place_forget()

    def display(self):
        # Create new window
        root = Toplevel(background='white')
        root.title(self.cs.na)

        # Create empty text array
        text_array = []
        for j in range(self.cs.dayn + 1):
            column = []
            for i in range(self.cs.pdn_per_day + 1):
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
                        e_in.insert('end', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[(j_in - 1) * self.cs.pdn_per_day +
                                                                        (i_in - 1)] + '\n')
                        e_in.tag_add('slot_No', '1.0', '1.1')
                        e_in.tag_configure('slot_No', foreground='red')

                        e_in.configure(bg=self.cs.get_color(j_in - 1,  i_in - 1))

                        for lsni, lsn in enumerate(self.cs[j_in - 1, i_in - 1].lsns):
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
                        e_in.insert('end', self.cs.time_list[j_in - 1])
            disable_text_array()

        def switch_two_slots():
            tg1 = switch_l_entry1.get().upper()
            tg2 = switch_l_entry2.get().upper()
            index1 = 'ABCDEFGHIJKLMNOPQRSTUVWXY'.find(tg1)
            index2 = 'ABCDEFGHIJKLMNOPQRSTUVWXY'.find(tg2)

            self.cs.switch_two_time_slots(index1, index2)

            clear_text_array()
            insert_form()

        def switch_two_sessions():
            sni1 = int(switch_n_entry1.get())
            sni2 = int(switch_n_entry2.get())

            if not self.cs.switch_two_sns(sni1, sni2):
                messagebox.showwarning(TR.warning, message=TR.cannot_switch)

            clear_text_array()
            insert_form()

        def export_csv():
            saving_path = filedialog.asksaveasfilename(initialfile=TR.export_csv_name + f'{self.cs.na}.csv',
                                                       title=TR.export_as_csv,
                                                       filetypes=(("csv files", "*.csv"),))
            if saving_path:
                self.cs.save_as_csv(saving_path)

        '''def save_draft():
            saving_path = filedialog.asksaveasfilename(initialfile=TR.save_draft_name + f'{self.cs.na}.txt',
                                                       title=TR.save_as_draft,
                                                       filetypes=(("txt file", "*.txt"),))
            if saving_path:
                try:
                    self.cs.serialize(saving_path)
                except PermissionError:
                    print("The file is being operated by another APP")'''

        def inspect_conflict():
            conflicts = self.cs.inspect()
            if not conflicts:
                message = TR.no_conflict
            else:
                message = ''
                for conflict in conflicts:
                    message += f'{conflict[0]}: {"".join([repr(inst) for inst in conflict[1]])}\n'
            messagebox.showinfo(TR.conflicts, message, parent=root)

        def cross_inspect():
            all_conflicts = self.cs.cross_inspect()
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
            self.cs.cross_adjust()
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

        #  the export csv button
        save_button = Button(root, text=TR.export_as_csv, command=export_csv)
        save_button.grid(row=6, column=7, sticky='WNE')

    def ask_destroy(self):
        if messagebox.askokcancel(title=TR.warning, message='Delete this course system?'):
            self.destroy()

    def destroy(self):
        page.forget_cs(self.cs.na)
        del self.cs
        self.button_frame.destroy()
        super().destroy()


class CentralPage(Frame):
    def debug(self):
        debug_msg = simpledialog.askstring(title='DEBUG', prompt='Method Name::arg1, arg2, arg3, ...')
        method_name = debug_msg.split('::')[0]
        args = debug_msg.split('::')[1].split(', ')
        getattr(self, method_name)(*args)

    def __init__(self, master: Tk, **kw):
        super(CentralPage, self).__init__(master, **kw)
        self.pack(fill='both', expand='yes')

        debug_button = Button(self, text='DEBUG', command=self.debug)
        debug_button.place(relx=0, rely=1, anchor='sw')

        # Front Page
        title = Label(self, text=TR.title, style='1.TLabel')
        title.place(x=0, y=0, height=50, width=550)

        self.schoolLabel = Label(self, text='Current School:', style='3.TLabel')
        self.schoolLabel.place(x=0, y=40, width=600, height=25)

        self.create_sch_b = Button(self, text=TR.new_sch, command=self.create_sch)
        self.create_sch_b.place(x=7, y=70, width=140)

        self.import_sch_b = Button(self, text=TR.import_sch, command=self.import_sch)
        self.import_sch_b.place(x=157, y=70, width=140)

        self.save_sch_b = Button(self, text=TR.save_sch, command=self.save_sch)
        self.save_sch_b.place(x=307, y=70, width=140)

        self.discharge_sch_b = Button(self, text=TR.close_sch, command=self.close_sch)
        self.discharge_sch_b.place(x=457, y=70, width=140)

        self.courseSystemFrame = LabelFrame(self, text=TR.course_systems)
        self.courseSystemFrame.place(x=5, y=110, width=165, height=300)

        self.create_cs_b = Button(self.courseSystemFrame, text=TR.create_cs, command=self.create_cs)
        self.create_cs_b.place(x=0, y=0)
        self.create_cs_b.configure(state='disabled')

        self.tableFormatFrame = LabelFrame(self, text=TR.table_format)
        self.tableFormatFrame.place(x=200, y=110, width=400, height=300)

        '''about_info = Text(self, autostyle=False, height=4, width=29, font=('Times New Roman', 12), relief='flat')
        about_info.insert('end', TR.about)
        about_info.place(x=460, y=40)
        about_info.configure(state='disabled')'''

        self.csInfoFrames: dict[str, CSInfoFrame] = {}
        self.sch = None

    @property
    def sch(self):
        return self._sch

    @sch.setter
    def sch(self, new_sch):
        self._sch = new_sch
        if new_sch is None:
            self.create_sch_b.configure(state='activated')
            self.import_sch_b.configure(state='activated')
            self.save_sch_b.configure(state='disabled')
            self.discharge_sch_b.configure(state='disabled')
            self.create_cs_b.configure(state='disabled')
        else:
            self.create_sch_b.configure(state='disabled')
            self.import_sch_b.configure(state='disabled')
            self.save_sch_b.configure(state='activated')
            self.discharge_sch_b.configure(state='activated')
            self.create_cs_b.configure(state='activated')

    def _add_cs(self, new_cs_name: str):
        """Add a course system to this school, add corresponding buttons"""
        assert self.sch is not None
        new_cs = self.sch.add_cs(new_cs_name, 5, 5)
        new_cs_frame = CSInfoFrame(self, x=200, y=110, width=400, height=300, cs=new_cs)  # create cs frame
        self.csInfoFrames[new_cs_name] = new_cs_frame  # archive cs frame

        # create button frame
        button_frame = Frame(self.courseSystemFrame)
        button_frame.place(x=0, y=int(self.create_cs_b.place_info()['y']), width=161, height=30)
        # create show_cs button
        new_cs_button = Button(button_frame, text=new_cs_name, style='CS.TButton', command=new_cs_frame.show)
        new_cs_button.place(x=0, y=0, width=125, height=30)
        # create destroy_cs button
        del_cs_button = Button(button_frame, text='X', style='CS.TButton', command=new_cs_frame.ask_destroy)
        del_cs_button.place(x=126, y=0, width=35, height=30)

        new_cs_frame.button_frame = button_frame
        self.create_cs_b.place(x=0, y=int(self.create_cs_b.place_info()['y']) + 30)  # move create_cs button

    def forget_cs(self, del_cs_name):
        """forget a course system (this will be executed after a course system is destroyed)"""
        del self.csInfoFrames[del_cs_name]  # delete the frame from archive
        self.create_cs_b.place(x=0, y=int(self.create_cs_b.place_info()['y']) - 30)  # move create_cs button

    def create_cs(self):
        """feature for users to create new course system"""
        assert self.sch is not None
        new_cs_name = simpledialog.askstring(title=TR.new_course_system,
                                             prompt=TR.ask_cs_name,
                                             parent=self.master)
        if new_cs_name:
            # check if exist...
            self._add_cs(new_cs_name)

    def create_sch(self):
        """feature for users to create a school"""
        # ask for school name
        name = simpledialog.askstring(title=TR.welcome,
                                      prompt=TR.ask_school,
                                      parent=self.master)
        self.master.lift()  # keep the window on the top

        if not name:
            name = TR.anonymous_school
        self.sch = GUISchool(name)

        self.schoolLabel = Label(self, text=f'Current School: {name}', style='3.TLabel')
        self.schoolLabel.place(x=0, y=40, width=600, height=25)

    def import_sch(self):
        """feature for users to import a school's course course arrangement from draft"""
        print('Not yet implemented')

    def save_sch(self):
        """feature for users to save a school's course arrangement"""
        print('Not yer implemented')

    def close_sch(self):
        """feature for users to discharge a school's course arrangement"""
        for cs_frame in tuple(self.csInfoFrames.values()):
            cs_frame.destroy()
        self.sch = None


window = Tk()
window.title('ACAS')
window.geometry('700x450')
window.resizable(0, 0)

s = Style()
s.theme_use('flatly')
s.configure('TLabelframe.Label', font=('Arial', 15), background='white', foreground='black')
s.configure('TLabelframe', background='white', borderwidth=2, bordercolor='black')
s.configure('TFrame', background='white')
s.configure('test.TFrame', background='blue')
s.configure('CS.TButton', background='#c9e3cc', foreground='black')
s.configure('TButton', background='white', foreground='black')
s.configure('1.TLabel', background='white', font=('Arial', 20), foreground='black')
s.configure('2.TLabel', background='white', font=('Arial', 10), foreground='black')  # Info path, state
s.configure('3.TLabel', background='white', font=('Arial', 15), foreground='black')  # School Label
s.configure('Horizontal.TProgressbar', background='white')

page = CentralPage(window)
'''def motion(event):
    x, y = event.x, event.y
    print('           \r', end='')
    print('{}, {}'.format(x, y), end='')


window.bind('<Motion>', motion)'''
window.mainloop()
