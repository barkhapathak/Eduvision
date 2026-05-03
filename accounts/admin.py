from django.contrib import admin
from .models import (
    Student, Teacher,
    Course, Subject, CourseSubject,
    TeacherAssignment, Marks, Attendance, Performance, Assignment
)

admin.site.register(Student)
admin.site.register(Teacher)

admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(CourseSubject)

admin.site.register(TeacherAssignment)

admin.site.register(Marks)
admin.site.register(Attendance)
admin.site.register(Performance)

admin.site.register(Assignment)
