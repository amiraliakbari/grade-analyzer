#!/usr/bin/env python
import re
import glob


class ObjectManager(object):
    _object_list = {}

    def __init__(self, pk):
        self.pk = pk

        pk = self.pk
        if pk is None:
            raise ValueError
        self._object_list[pk] = self

    def __unicode__(self):
        return u'{0}#{1}'.format(self.__class__.__name__, self.pk)

    @classmethod
    def all_objects(cls):
        return cls._object_list.values()

    @classmethod
    def get_object(cls, pk, create=False):
        if isinstance(pk, cls):
            return pk
        if create:
            if not pk in cls._object_list:
                cls._object_list[pk] = cls(pk=pk)
        return cls._object_list[pk]


class Room(ObjectManager):
    _object_list = {}

    def __init__(self, pk):
        super(Room, self).__init__(pk)
        self.dormitory = ''
        self.students = []

    def add_student(self, student):
        student = Student.get_object(student, create=True)
        self.students.append(student)


class Student(ObjectManager):
    _object_list = {}

    def __init__(self, pk):
        super(Student, self).__init__(pk)
        self.grades = []

    def __unicode__(self):
        return u'{0}: {1}'.format(self.pk, u','.join(g.__unicode__() for g in self.grades))


class ExamGrade(object):
    def __init__(self, student, exam='', absent=False):
        self.is_absent = absent
        self.question_grades = []
        self._student = None
        self.exam = exam

        #initialization
        self.student = student

    def __unicode__(self):
        if self.is_absent:
            return u'{0} ({1}): ABSENT'.format(self.student.pk, self.exam)
        return u'{0} ({1}): {2}'.format(self.student.pk, self.exam, str(self.question_grades))

    def add_grade(self, grade):
        if self.is_absent:
            raise ValueError
        self.question_grades.append(grade)

    @property
    def student(self):
        return self._student

    @student.setter
    def student(self, new_student):
        self._student = new_student
        self._student.grades.append(self)

    @classmethod
    def create(cls, stdid, exam=''):
        return ExamGrade(Student.get_object(stdid, create=True), exam=exam)


class FileReader(object):
    OPTION_LINE_RE = re.compile(r"^#!\s*(.+?)\s*='(.+?)'\s*$")

    def __init__(self, filename):
        self.opts = {
            'type': 'grades',
            'exam': '',
            'dormitory': '',
            'sep': ' ',
            'absent': 'ab',
            'ignore': r'^\w*$',
            'cols': 'sum',
        }
        print('Reading file: {0}...'.format(filename))
        self.read_file(filename)
    
    def read_option_line(self, l):
        """
            :param str l: line to be read
        """
        m = self.OPTION_LINE_RE.match(l)
        if not l[2:].strip():
            return
        if not m:
            raise ValueError
        k = m.group(1).lower()
        v = m.group(2)
        if not k in self.opts:
            raise ValueError('Invalid option name: {0}.'.format(k))
        self.opts[k] = v

    def read_line(self, l):
        """
            :param str l: line to be read
        """
        l = l.strip()
        if l.startswith('#!'):
            self.read_option_line(l)
            return

        if re.match(self.opts['ignore'], l):
            return

        tp = self.opts['type']
        if tp == 'grades':
            m = re.match(self.opts['absent'], l)
            if m:
                stdid = int(m.group(1))
                e = ExamGrade.create(stdid, exam=self.opts['exam'])
                e.is_absent = True
                return

            cols = self.opts['cols'].split(',')
            grades = l.split(self.opts['sep'])

            pid = cols.index('id')
            if not pid < len(grades):  # TODO: optional columns
                pid = pid - len(grades)
            e = ExamGrade.create(grades[pid], exam=self.opts['exam'])
            for i, c in enumerate(cols):
                if re.match(r'q\d+', c):
                    qid = int(c[1:])
                    e.add_grade(grades[i])
            #print(unicode(e))
        elif tp == 'dormitory':
            room, stds = l.split('=')
            r = Room.get_object(room, create=True)
            r.dormitory = self.opts['dormitory']
            for std in stds.split(','):
                r.add_student(std)
        else:
            raise ValueError

    def read_file(self, filename):
        for l in open(filename):
            self.read_line(l)


if __name__ == '__main__':
    FileReader('data/tg1.txt')
    FileReader('data/tg2.txt')
    FileReader('data/tg3.txt')

    if False:
        for s in Student.all_objects():
            print(unicode(s))

    if True:
        for r in Room.all_objects():
            #print type(r), r
            title = ' ' + unicode(r) + ' ' + r.dormitory + ' '
            print('')
            print('*'*len(title))
            print(title)
            print('*'*len(title))
            for s in r.students:
                print('### {0} ###'.format(s.pk))
                for eg in s.grades:
                    print(u'{0}: {1}'.format(eg.exam, str(eg.question_grades)))
