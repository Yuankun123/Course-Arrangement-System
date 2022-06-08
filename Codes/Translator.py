class Translator:
    title = ['Automatic Course Arrangement System',
             '自动排课系统']
    about = ['Website: https://github.com/Yuankun123/Course-Arrangement-System.git\n'
             'Open Source under MIT license\n'
             'E-Mail: Kunko2005@hotmail.com',
             '网站：https://github.com/Yuankun123/Course-Arrangement-System.git\n'
             '在 MIT license 下开源\n'
             '邮箱：Kunko2005@hotmail.com']
    welcome = ['Welcome',
               '欢迎']
    ask_school = ['Please indicate the name of your school',
                  '请输入您的学校名称']
    anonymous_school = ['Anonymous School',
                        '未知学校']
    course_systems = ['Course Systems',
                      '课程系统']
    table_format = ['Table Format',
                    '课表格式']
    add = ['Add...',
           '添加...']
    import_from_draft = ['Import From Draft',
                         '从草稿导入']
    new_course_system = ['New Course System',
                         ]
    ask_cs_name = ['Please enter the name of this course system',
                   ]
    choose_file = ['Choose a file',
                   ]
    detail_info = ['Detail Information: ',
                   ]
    course_info_path = ['Course information file path: ',
                        ]
    import_course_info_file = ['Import course information file',
                               ]
    start_arr = ['Start arranging',
                 ]
    display = ['Display',
               ]
    cannot_switch = ['Cannot switch because two sessions are in different modules',
                     ]
    warning = ['Warning',
               ]
    export_csv_name = ['Course_Arrangement_for_',
                       ]
    export_as_csv = ['Export as CSV',
                     ]
    save_draft_name = ['Arrangement_Draft_for_',
                       ]
    save_as_draft = ['Save as draft',
                     ]
    no_conflict = ['No Conflict...PnP',
                   ]
    conflicts = ['Conflicts',
                 ]
    conflicts_with = ['conflicts with',
                      ]
    switch_two_slots = ['Switch two time slots',
                        ]
    switch_two_sessions = ['Switch two sessions',
                           ]
    inspect = ['Inspect',
               ]
    cross_inspect = ['Cross-Inspect',
                     ]
    cross_adjust = ['Cross-Adjust',
                    ]

    def __init__(self, language=0):
        self.lan = language

    def __getattribute__(self, item):
        if item == 'lan':
            return super().__getattribute__(item)

        # this allows the translator the select the right version for its language.
        return super().__getattribute__(item)[self.lan]


TR = Translator(0)
if __name__ == '__main__':
    class _Client:  # hide code
        tr1 = Translator(0)  # English translator
        tr2 = Translator(1)  # Chinese translator
        print(tr1.title, tr2.title)
