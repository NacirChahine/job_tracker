from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from .models import JobApplication
from .forms import (
    JobApplicationForm,
    JobApplicationEditForm,
    StatusUpdateForm,
    NotesEditForm,
    RegistrationForm,
)


# ── Auth Views ──────────────────────────────────────────────────────────────


def register_view(request):
    if request.user.is_authenticated:
        return redirect("tracker:dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect("tracker:dashboard")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("tracker:dashboard")

    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next") or "tracker:dashboard"
            return redirect(next_url)
        error = "Invalid username or password."

    return render(request, "registration/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("tracker:login")


# ── Dashboard ───────────────────────────────────────────────────────────────


@login_required
def dashboard(request):
    applications = JobApplication.objects.filter(user=request.user)
    form = JobApplicationForm()
    return render(request, "dashboard.html", {
        "applications": applications,
        "form": form,
        "job_statuses": JobApplication.STATUS_CHOICES,
    })


# ── HTMX Partials ───────────────────────────────────────────────────────────


@login_required
def job_list(request):
    applications = JobApplication.objects.filter(user=request.user)

    search = request.GET.get("search", "").strip()
    if search:
        applications = applications.filter(
            Q(company_name__icontains=search)
            | Q(position__icontains=search)
        )

    status_filter = request.GET.get("status", "").strip()
    if status_filter and status_filter in dict(JobApplication.STATUS_CHOICES):
        applications = applications.filter(status=status_filter)

    return render(request, "partials/job_list.html", {"applications": applications})



@login_required
def job_create(request):
    if request.method == "POST":
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            return render(request, "partials/job_item.html", {"job": job})
        return render(request, "partials/job_form.html", {"form": form})
    return HttpResponse(status=405)


@login_required
def job_detail(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)
    return render(request, "partials/job_item.html", {"job": job})


@login_required
def job_update(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method in ("POST", "PUT", "PATCH"):
        form = JobApplicationEditForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return render(request, "partials/job_item.html", {"job": job})
        return render(request, "partials/job_form.html", {"form": form, "job": job, "edit": True})
    return HttpResponse(status=405)


@login_required
def job_edit_form(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)
    form = JobApplicationEditForm(instance=job)
    return render(request, "partials/job_form.html", {"form": form, "job": job, "edit": True})


@login_required
def job_status_update(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method in ("POST", "PATCH"):
        form = StatusUpdateForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return render(request, "partials/job_item.html", {"job": job})
    return HttpResponse(status=405)


@login_required
def job_notes_edit(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == "GET":
        form = NotesEditForm(instance=job)
        return render(request, "partials/notes_edit.html", {"form": form, "job": job})
    if request.method in ("POST", "PUT"):
        form = NotesEditForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return render(request, "partials/job_item.html", {"job": job})
        return render(request, "partials/notes_edit.html", {"form": form, "job": job})
    return HttpResponse(status=405)


@login_required
def job_delete(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == "DELETE":
        job.delete()
        return HttpResponse(status=200)
    return HttpResponse(status=405)
