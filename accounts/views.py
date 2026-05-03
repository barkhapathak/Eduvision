from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import pandas as pd
from functools import wraps
from django.http import HttpResponseForbidden
from django.http import JsonResponse
import json
from .models import Teacher, Student
from .models import *
from .ml_utils import predict_performance, load_model, get_reason


# =========================
# 🏠 HOME
# =========================
def home(request):
    return render(request, 'accounts/home.html')


# =========================
# 🔐 AUTH DECORATORS
# =========================
def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not Teacher.objects.filter(user=request.user).exists():
            return HttpResponseForbidden("Teachers only")
        return view_func(request, *args, **kwargs)
    return _wrapped


def student_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not Student.objects.filter(user=request.user).exists():
            return HttpResponseForbidden("Students only")
        return view_func(request, *args, **kwargs)
    return _wrapped


# =========================
# 🔐 LOGIN
# =========================
def login_view(request):

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            if Student.objects.filter(user=user).exists():
                return redirect('student_dashboard')

            elif Teacher.objects.filter(user=user).exists():
                return redirect('teacher_dashboard')

            else:
                return redirect('home')

        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid email or password'
            })

    return render(request, 'accounts/login.html')


# =========================
# 🎓 STUDENT SIGNUP
# =========================
def student_signup(request):

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        degree = request.POST.get('degree')
        smartid = request.POST.get('smartid')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            return render(request, 'accounts/stu_signup.html', {
                'error': 'Email already registered'
            })

        if Student.objects.filter(smartid=smartid).exists():
            return render(request, 'accounts/stu_signup.html', {
                'error': 'Smart ID already exists'
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        Student.objects.create(
            user=user,
            degree=degree,
            smartid=smartid
        )

        return redirect('login')

    return render(request, 'accounts/stu_signup.html')


# =========================
# 👨‍🏫 TEACHER SIGNUP
# =========================
def teacher_signup(request):

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        department = request.POST.get('department')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            return render(request, 'accounts/teacher_signup.html', {
                'error': 'Email already registered'
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        Teacher.objects.create(
            user=user,
            department=department
        )

        return redirect('login')

    return render(request, 'accounts/teacher_signup.html')


# =========================
# 👨‍🏫 TEACHER DASHBOARD
# =========================
@teacher_required
def teacher_dashboard(request):
    load_model()

    excellent = []
    average = []
    poor = []

    show_result = False
    course_subjects = CourseSubject.objects.all()

    if request.method == "POST":
        show_result = True

        cs_id = request.POST.get("course_subject_id")

        if not cs_id:
            return render(request, 'accounts/teacher_dashboard.html', {
                'course_subjects': course_subjects,
                'show_result': False
            })

        # ✅ Selected subject
        course_subject = CourseSubject.objects.get(id=cs_id)

        # ✅ Filter students by course (VERY IMPORTANT)
        students = Student.objects.filter(degree=course_subject.course.course_name)

        for student in students:

            # ✅ FILTER BY SELECTED SUBJECT ONLY
            marks = Marks.objects.filter(student=student, course_subject=course_subject)
            attendance = Attendance.objects.filter(student=student, course_subject=course_subject)
            assignment = Assignment.objects.filter(student=student, course_subject=course_subject)

            avg_marks = sum([m.marks for m in marks]) / len(marks) if marks else 0
            avg_att = sum([a.attendance_percentage for a in attendance]) / len(attendance) if attendance else 0
            avg_assign = sum([a.assignment_marks for a in assignment]) / len(assignment) if assignment else 0

            # ❌ skip empty students
            if avg_marks == 0 and avg_att == 0 and avg_assign == 0:
                continue

            # ✅ prediction
            category = predict_performance(avg_att, avg_marks, avg_assign)

            # ✅ save
            Performance.objects.update_or_create(
                student=student,
                defaults={
                    'avg_marks': avg_marks,
                    'avg_attendance': avg_att,
                    'category': category
                }
            )

            # ✅ grouping
            if category == "Excellent":
                excellent.append(student.user.first_name)

            elif category == "Average":
                average.append(student.user.first_name)

            else:
                reason = get_reason(avg_att, avg_marks, avg_assign)
                poor.append({
                    "name": student.user.first_name,
                    "reason": reason
                })

    return render(request, 'accounts/teacher_dashboard.html', {
        'excellent': excellent,
        'average': average,
        'poor': poor,
        'excellent_count': len(excellent),
        'average_count': len(average),
        'poor_count': len(poor),
        'show_result': show_result,
        'course_subjects': course_subjects,  # ✅ REQUIRED
    })

# =========================
# 🚪 LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect('home')


# =========================
# 📊 UPLOAD MARKS
# =========================
@teacher_required
def upload_marks(request):

    if request.method == "POST":
        file = request.FILES.get('file')
        course_name = request.POST.get('course')
        subject_name = request.POST.get('subject')

        if not file:
            return redirect('teacher_dashboard')

        teacher = Teacher.objects.filter(user=request.user).first()
        course = Course.objects.filter(course_name=course_name).first()
        subject = Subject.objects.filter(subject_name=subject_name).first()

        course_subject = CourseSubject.objects.filter(
            course=course,
            subject=subject
        ).first()

        df = pd.read_excel(file)

        for _, row in df.iterrows():
            student = Student.objects.filter(smartid=row.get('smartid')).first()

            if student:
                Marks.objects.create(
                    student=student,
                    course_subject=course_subject,
                    teacher=teacher,
                    marks=row.get('marks'),
                    max_marks=100
                )

    return redirect('teacher_dashboard')


# =========================
# 📊 UPLOAD ATTENDANCE
# =========================
@teacher_required
def upload_attendance(request):

    if request.method == "POST":
        file = request.FILES.get('file')
        course_name = request.POST.get('course')
        subject_name = request.POST.get('subject')

        teacher = Teacher.objects.filter(user=request.user).first()
        course = Course.objects.filter(course_name=course_name).first()
        subject = Subject.objects.filter(subject_name=subject_name).first()

        course_subject = CourseSubject.objects.filter(
            course=course,
            subject=subject
        ).first()

        df = pd.read_excel(file)

        for _, row in df.iterrows():
            student = Student.objects.filter(smartid=row.get('smartid')).first()

            if student:
                Attendance.objects.create(
                    student=student,
                    course_subject=course_subject,
                    teacher=teacher,
                    attendance_percentage=row.get('attendance')
                )

    return redirect('teacher_dashboard')


# =========================
# 📊 UPLOAD ASSIGNMENT
# =========================
@teacher_required
def upload_assignment(request):

    if request.method == "POST":
        file = request.FILES.get('file')
        course_name = request.POST.get('course')
        subject_name = request.POST.get('subject')

        teacher = Teacher.objects.filter(user=request.user).first()
        course = Course.objects.filter(course_name=course_name).first()
        subject = Subject.objects.filter(subject_name=subject_name).first()

        course_subject = CourseSubject.objects.filter(
            course=course,
            subject=subject
        ).first()

        df = pd.read_excel(file)

        for _, row in df.iterrows():
            student = Student.objects.filter(smartid=row.get('smartid')).first()

            if student:
                Assignment.objects.create(
                    student=student,
                    course_subject=course_subject,
                    teacher=teacher,
                    assignment_marks=row.get('assignment_marks')
                )

    return redirect('teacher_dashboard')


# =========================
# 🎓 STUDENT DASHBOARD
# =========================
@student_required
def student_dashboard(request):

    student = Student.objects.get(user=request.user)

    # ✅ Get student's course
    course = Course.objects.filter(course_name=student.degree).first()

# ✅ Only subjects of that course
    course_subjects = CourseSubject.objects.filter(course=course).select_related('subject')
    
    data = []

    # ✅ SUBJECT DATA
    
    for cs in course_subjects:

      marks_obj = Marks.objects.filter(student=student, course_subject=cs).first()
      attendance_obj = Attendance.objects.filter(student=student, course_subject=cs).first()
      assignment_obj = Assignment.objects.filter(student=student, course_subject=cs).first()

    # 🚨 SKIP if NO DATA at all
      if not marks_obj and not attendance_obj and not assignment_obj:
           continue

      marks = marks_obj.marks if marks_obj else 0
      attendance = attendance_obj.attendance_percentage if attendance_obj else 0
      assignment = assignment_obj.assignment_marks if assignment_obj else 0

      avg = (marks + attendance + assignment) / 3

      data.append({
        'subject': cs.subject.subject_name,
        'marks': marks,
        'attendance': attendance,
        'assignment': assignment,
        'avg': avg
     })

    performance = Performance.objects.filter(student=student).first()

    # 🔥 totals
    total_marks = sum([d['marks'] for d in data]) / len(data) if data else 0
    total_att = sum([d['attendance'] for d in data]) / len(data) if data else 0
    total_assign = sum([d['assignment'] for d in data]) / len(data) if data else 0

    # 🔥 category
    if performance:
        category = performance.category
    else:
        category = predict_performance(total_att, total_marks, total_assign)

    # 🔥 reason
    reason = get_reason(total_att, total_marks, total_assign)

    # 🔥 suggestions
    suggestions = []
    if total_att < 60:
        suggestions.append("Attend more classes regularly")
    if total_marks < 50:
        suggestions.append("Focus on studying core subjects")
    if total_assign < 50:
        suggestions.append("Submit assignments on time")

    # 🔥 message
    if category == "Excellent":
        message = "Keep up the great work!"
    elif category == "Average":
        message = "You're doing good, but you can improve more!"
    else:
        message = "Don't worry, focus and improve step by step!"

    # =========================
    # 🆕 NEW FEATURES
    # =========================

    # ⭐ strongest & weakest
    strongest_subject = max(data, key=lambda x: x['avg']) if data else None
    weakest_subject = min(data, key=lambda x: x['avg']) if data else None

    # 🔴 weak subjects list
    weak_subjects = []

    for d in data:
        if d['marks'] > 0 and (d['marks'] < 40 or d['attendance'] < 50):
         weak_subjects.append(d)
    
    seen = set()
    unique_weak = []

    for w in weak_subjects:
     if w['subject'] not in seen:
        unique_weak.append(w)
        seen.add(w['subject'])

    weak_subjects = unique_weak



    # 📊 graph data
    subjects = [d['subject'] for d in data]
    marks_data = [d['marks'] for d in data]
    attendance_data = [d['attendance'] for d in data]
    assignment_data = [d['assignment'] for d in data]

    # 🏆 rank system
    all_students = Student.objects.all()
    student_scores = []

    for s in all_students:
        marks = Marks.objects.filter(student=s)
        avg = sum([m.marks for m in marks]) / len(marks) if marks else 0
        student_scores.append((s, avg))

    student_scores.sort(key=lambda x: x[1], reverse=True)

    rank = None
    for i, (s, _) in enumerate(student_scores, start=1):
        if s == student:
            rank = i
            break

    # 📊 class average
    class_avg = sum([score for _, score in student_scores]) / len(student_scores) if student_scores else 0

    return render(request, 'accounts/student_dashboard.html', {
        'data': data,
        'performance': performance,
        'category': category,
        'reason': reason,
        'suggestions': suggestions,
        'message': message,
        'att': total_att,
        'marks': total_marks,
        'assign': total_assign,
        'strongest_subject': strongest_subject,
        'weakest_subject': weakest_subject,

        # 🆕 NEW
        'weak_subjects': weak_subjects,
        'subjects': subjects,
        'marks_data': marks_data,
        'attendance_data': attendance_data,
        'assignment_data': assignment_data,
        'rank': rank,
        'class_avg': class_avg
    })
# chatbot 

def chatbot_response(request):
    if request.method == "POST":
        message = request.POST.get("message").lower()
        student = Student.objects.get(user=request.user)

        data = []
        weak_subjects = []
        strong_subject = None
        max_marks = -1

        course_subjects = CourseSubject.objects.filter(course__course_name=student.degree)

        for cs in course_subjects:
            marks_obj = Marks.objects.filter(student=student, course_subject=cs).first()
            attendance_obj = Attendance.objects.filter(student=student, course_subject=cs).first()

            marks = marks_obj.marks if marks_obj else 0
            attendance = attendance_obj.attendance_percentage if attendance_obj else 0

            data.append((cs.subject.subject_name, marks, attendance))

            # detect weak subjects
            if marks < 40 or attendance < 60:
                weak_subjects.append(cs.subject.subject_name)

            # detect strongest
            if marks > max_marks:
                max_marks = marks
                strong_subject = cs.subject.subject_name

        reply = "I didn't understand. Try asking about performance, weak subjects, or improvement."

        # 🔥 SMART RESPONSES

        if "performance" in message:
            avg = sum([d[1] for d in data]) / len(data) if data else 0
            if avg >= 75:
                reply = "Excellent performance! Keep it up 💯"
            elif avg >= 50:
                reply = "Average performance. You can improve."
            else:
                reply = "Your performance is low. Focus more on weak areas."

        elif "weak" in message:
            if weak_subjects:
                reply = "Weak subjects: " + ", ".join(weak_subjects)
            else:
                reply = "No weak subjects. You're doing great!"

        elif "strong" in message or "best" in message:
            reply = f"Your strongest subject is {strong_subject}"

        elif "improve" in message:
            tips = []
            if weak_subjects:
                tips.append("Focus on: " + ", ".join(weak_subjects))
            tips.append("Maintain attendance above 75%")
            tips.append("Practice assignments regularly")
            reply = " | ".join(tips)

        elif "attendance" in message:
            low_att = [d[0] for d in data if d[2] < 75]
            if low_att:
                reply = "Low attendance in: " + ", ".join(low_att)
            else:
                reply = "Your attendance is good in all subjects!"

        elif "marks" in message:
            msg = ""
            for d in data:
                msg += f"{d[0]}: {d[1]} marks | "
            reply = msg

        return JsonResponse({"response": reply})