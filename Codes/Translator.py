class Translator:
    title = ['Automatic Course Arrangement System', '自动排课系统']
    about = ['Author: Yuankun Zou\nE-Mail: Kunko2005@hotmail.com\nAll Rights Reserved',
             '作者：邹元堃\n邮箱：Kunko2005@hotmail.com\n保留所有权利']
    welcome = ['Welcome to use ACAS2.0.', '欢迎']
    ask_school = ['Please indicate the name of your school']
    anonymous_school = ['Anonymous School']

    def __init__(self, language=0):
        self.lan = language

    def __getattribute__(self, item):
        if item == 'lan':
            return super().__getattribute__(item)

        # this allows the translator the select the right version for its language.
        return super().__getattribute__(item)[self.lan]


if __name__ == '__main__':
    class _Client:  # hide code
        tr1 = Translator(0)  # English translator
        tr2 = Translator(1)  # Chinese translator
        print(tr1.title, tr2.title)
