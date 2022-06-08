from tkinter import *
from ttkbootstrap import *
from tkinter import filedialog, simpledialog

from Functions import School, CourseSystem
from Translator import TR
from CourseSystemGUI import CSInfoFrame


class CentralPage(Frame):
    def __init__(self, master: Tk, **kw):
        super(CentralPage, self).__init__(master, **kw)
        self.pack(fill='both', expand='yes')

        # Front Page
        title = Label(self, text=TR.title, style='1.TLabel')
        title.place(x=0, y=0, height=50, width=550)

        self.courseSystemFrame = LabelFrame(self, text=TR.course_systems)
        self.courseSystemFrame.place(x=5, y=110, width=165, height=300)

        self.tableFormatFrame = LabelFrame(self, text=TR.table_format)
        self.tableFormatFrame.place(x=200, y=110, width=400, height=300)

        self.courseSystemOperateFrame = Frame(self.courseSystemFrame)
        self.courseSystemOperateFrame.place(x=0, y=0)

        create_cs_b = Button(self.courseSystemOperateFrame, text=TR.add, command=self.create_cs)
        create_cs_b.grid(column=0, row=1, sticky='w')

        import_cs_b = Button(self.courseSystemOperateFrame, text=TR.import_from_draft, command=self.import_cs)
        import_cs_b.grid(column=0, row=0, columnspan=2)

        about_info = Text(self, autostyle=False, height=4, width=29, font=('Times New Roman', 12), relief='flat')
        about_info.insert('end', TR.about)
        about_info.place(x=460, y=40)
        about_info.configure(state='disabled')

        # ask for school name
        name = simpledialog.askstring(title=TR.welcome,
                                      prompt=TR.ask_school,
                                      parent=self.master)
        self.master.lift()  # keep the window on the top

        if not name:
            name = TR.anonymous_school
        school_name = Label(self, text='For ' + name, style='3.TLabel')
        school_name.place(x=0, y=40, height=20, width=450)
        self.sch = School(name)

        # CourseSystem info frames
        self.csInfoFrames: list[CSInfoFrame] = []

    def create_cs(self):
        new_cs_name = simpledialog.askstring(title=TR.new_course_system,
                                             prompt=TR.ask_cs_name,
                                             parent=self.master)
        if new_cs_name:
            # check if exist...

            new_cs_frame = CSInfoFrame(self, x=200, y=110, width=400, height=300, cs=new_cs_name)
            self.csInfoFrames.append(new_cs_frame)
            new_cs_button = Button(self.courseSystemFrame, text=new_cs_name, style='CS.TButton',
                                   command=new_cs_frame.show)
            new_cs_button.place(x=0, y=int(self.courseSystemOperateFrame.place_info()['y']), width=161, height=30)
            self.courseSystemOperateFrame.place(x=0, y=int(self.courseSystemOperateFrame.place_info()['y']) + 30)

    def import_cs(self):
        open_path = filedialog.askopenfilename(title=TR.choose_file, filetypes=(("txt files", "*.txt"),))
        if open_path:
            new_cs = CourseSystem.deserialize(open_path)
            new_cs_frame = CSInfoFrame(self, x=200, y=110, width=400, height=300, cs=new_cs)
            self.csInfoFrames.append(new_cs_frame)
            new_cs_button = Button(self.courseSystemFrame, text=new_cs.na, style='CS.TButton',
                                   command=new_cs_frame.show)
            new_cs_button.place(x=0, y=int(self.courseSystemOperateFrame.place_info()['y']), width=161, height=30)
            self.courseSystemOperateFrame.place(x=0, y=int(self.courseSystemOperateFrame.place_info()['y']) + 30)


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
s.configure('2.TLabel', background='white', font=('Arial', 10), foreground='black')
s.configure('3.TLabel', background='#c9e3cc', font=('Times', 10, 'italic'), foreground='black')
s.configure('Horizontal.TProgressbar', background='white')

CentralPage(window)
'''def motion(event):
    x, y = event.x, event.y
    print('           \r', end='')
    print('{}, {}'.format(x, y), end='')


window.bind('<Motion>', motion)'''
window.mainloop()
