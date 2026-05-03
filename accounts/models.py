# Create your models here.
from django.db import models
from django.contrib.auth.models import User


# STUDENT MODEL
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100)
    smartid = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username


# TEACHER MODEL
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username



# 🟢 COURSE
class Course(models.Model):
    course_name = models.CharField(max_length=100)

    def __str__(self):
        return self.course_name


# 🟢 SUBJECT
class Subject(models.Model):
    subject_name = models.CharField(max_length=100)

    def __str__(self):
        return self.subject_name


# 🟢 COURSE-SUBJECT
class CourseSubject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course.course_name} - {self.subject.subject_name}"


# 🟢 TEACHER ASSIGNMENT
class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course_subject = models.ForeignKey(CourseSubject, on_delete=models.CASCADE)


# 🟢 MARKS
class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_subject = models.ForeignKey(CourseSubject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    marks = models.IntegerField()
    max_marks = models.IntegerField(default=100)


# 🟢 ATTENDANCE
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_subject = models.ForeignKey(CourseSubject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    attendance_percentage = models.FloatField()


# 🟢 PERFORMANCE
class Performance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    avg_marks = models.FloatField()
    avg_attendance = models.FloatField()
    category = models.CharField(max_length=50)


class Assignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_subject = models.ForeignKey(CourseSubject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    assignment_marks = models.FloatField()
    max_marks = models.FloatField(default=100)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.smartid} - {self.assignment_marks}"