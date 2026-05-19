from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import StudyPlan, Task


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    if request.method == "POST":
        subjects_input = request.POST.getlist('subjects')
        due_dates = request.POST.getlist('due_dates')
        subtopics_input = request.POST.getlist('subtopics')
        subtopic_counts = request.POST.getlist('subtopic_count')
        total_hours = int(request.POST.get('hours'))

        number_of_subjects = len(subjects_input)

        if number_of_subjects > 0:
            hours_per_subject = round(total_hours / number_of_subjects, 2)
        else:
            return render(request, 'index.html', {'error': 'Please add at least one subject'})

        StudyPlan.objects.filter(user=request.user).delete()
        Task.objects.filter(user=request.user).delete()

        for i, subject in enumerate(subjects_input):
            due_date = due_dates[i] if i < len(due_dates) and due_dates[i] else None

            StudyPlan.objects.create(
                user=request.user,
                subject_name=subject,
                hours_allocated=hours_per_subject,
                due_date=due_date
            )

            subtopics_text = subtopics_input[i].strip() if i < len(subtopics_input) else ""
            subtopic_count = subtopic_counts[i].strip() if i < len(subtopic_counts) else ""

            if subtopics_text:
                subtopic_list = [s.strip() for s in subtopics_text.split(",") if s.strip()]
            elif subtopic_count.isdigit():
                subtopic_list = [f"Topic {j+1}" for j in range(int(subtopic_count))]
            else:
                subtopic_list = ["Topic 1"]

            for topic in subtopic_list:
                Task.objects.create(
                    user=request.user,
                    subject=subject,
                    title=topic
                )

        return redirect('result')

    return render(request, 'index.html')


@login_required
def result(request):
    study_plan = StudyPlan.objects.filter(user=request.user)
    tasks = Task.objects.filter(user=request.user)

    detailed_plan = []

    for plan in study_plan:
        subject_tasks = tasks.filter(subject=plan.subject_name)
        subtopic_count = subject_tasks.count()

        if subtopic_count > 0:
            per_topic_hours = round(plan.hours_allocated / subtopic_count, 2)
        else:
            per_topic_hours = plan.hours_allocated

        detailed_plan.append({
            'subject': plan.subject_name,
            'subject_hours': plan.hours_allocated,
            'subtopics': subject_tasks,
            'per_topic_hours': per_topic_hours,
        })

    return render(request, 'result.html', {'detailed_plan': detailed_plan})

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = tasks.filter(completed=False).count()

    if total_tasks > 0:
        progress = int((completed_tasks / total_tasks) * 100)
    else:
        progress = 0

    subjects = {}

    subject_names = tasks.values_list('subject', flat=True).distinct()

    for subject in subject_names:
        subject_tasks = tasks.filter(subject=subject)
        subject_total = subject_tasks.count()
        subject_completed = subject_tasks.filter(completed=True).count()

        if subject_total > 0:
            subject_progress = int((subject_completed / subject_total) * 100)
        else:
            subject_progress = 0

        study_plan = StudyPlan.objects.filter(user=request.user, subject_name=subject).first()

        subjects[subject] = {
            'tasks': subject_tasks,
            'progress': subject_progress,
            'due_date': study_plan.due_date if study_plan else None,
            'hours': study_plan.hours_allocated if study_plan else 0,
            'topic_hours': round(study_plan.hours_allocated / subject_total, 2) if study_plan and subject_total > 0 else 0,
        }

    context = {
        'subjects': subjects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'progress': progress,
    }

    return render(request, 'dashboard.html', context)

@login_required
def add_task(request):
    if request.method == "POST":
        subject = request.POST.get('subject')
        title = request.POST.get('title')

        Task.objects.create(
            user=request.user,
            subject=subject,
            title=title
        )

    return redirect('dashboard')
    

@login_required
def complete_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    task.completed = True
    task.save()
    return redirect('dashboard')

@login_required
def toggle_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)

    if task.completed == False:
        task.completed = True
    else:
        task.completed = False

    task.save()
    return redirect('dashboard')

@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    task.delete()
    return redirect('dashboard')

@login_required
def edit_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)

    if request.method == "POST":
        task.title = request.POST.get("title")
        task.save()
        return redirect('dashboard')

    return render(request, 'edit_task.html', {'task': task})

from django.contrib.auth import logout

def custom_logout(request):
    logout(request)
    return render(request, 'logout_success.html')
