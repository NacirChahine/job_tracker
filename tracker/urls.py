from django.urls import path
from . import views

app_name = "tracker"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/create/", views.job_create, name="job_create"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/edit/", views.job_edit_form, name="job_edit_form"),
    path("jobs/<int:pk>/update/", views.job_update, name="job_update"),
    path("jobs/<int:pk>/status/", views.job_status_update, name="job_status_update"),
    path("jobs/<int:pk>/notes/", views.job_notes_edit, name="job_notes_edit"),
    path("jobs/<int:pk>/delete/", views.job_delete, name="job_delete"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
]
