# Job Application Tracker

A production-ready, secure, and performant web application for tracking job applications. Built with Django and HTMX following the "HTML over the wire" philosophy for a reactive SPA-like experience without a JavaScript framework.

## Tech Stack

- **Backend:** Django 5.1+ (Function-Based Views)
- **Frontend:** Django Templates + HTMX 2.x
- **Styling:** Bootstrap 5 (CDN)
- **Database:** SQLite

## Features

- User authentication (Register, Login, Logout)
- Strict data isolation — every query filtered by `request.user`
- Dynamic dashboard with HTMX partials
- Inline job application creation (prepends to list, clears form)
- Inline status updates via dropdown
- Inline editing of application details
- Inline notes editing
- Instant deletion with confirmation dialog
- Real-time search & filter (by company, position, status)

## Quick Start

```bash
# 1. Clone and enter the project
cd job_tracker_2

# 2. Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install django

# 4. Run migrations
python manage.py migrate

# 5. Start the development server
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser. Register a new account to get started.

## Project Structure

```
job_tracker_2/
├── job_tracker/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tracker/              # Main application
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── templates/
│   ├── base.html         # Main layout (HTMX + Bootstrap CDN)
│   ├── dashboard.html    # Authenticated main view
│   ├── registration/
│   │   ├── login.html
│   │   └── register.html
│   └── partials/
│       ├── job_list.html  # Loop container for job items
│       ├── job_item.html  # Individual card fragment
│       ├── job_form.html  # Form for creation & editing
│       └── notes_edit.html # Inline notes editor
├── manage.py
└── db.sqlite3
```

## HTMX Interactions

| Feature | Method | HTMX Attributes | Target |
|---------|--------|-----------------|--------|
| Create Job | POST | `hx-post`, `hx-swap="afterbegin"` | `#job-list` |
| Status Update | POST | `hx-post`, `hx-swap="outerHTML"` | `#job-{id}` |
| Edit Form | GET | `hx-get`, `hx-swap="outerHTML"` | `#job-{id}` |
| Save Edit | POST | `hx-post`, `hx-swap="outerHTML"` | `#job-{id}` |
| Edit Notes | GET | `hx-get`, `hx-swap="innerHTML"` | `#notes-{id}` |
| Save Notes | POST | `hx-post`, `hx-swap="outerHTML"` | `#job-{id}` |
| Delete | DELETE | `hx-delete`, `hx-confirm`, `hx-swap="outerHTML swap:0.3s"` | `closest .job-item` |
| Search | GET | `hx-trigger="keyup changed delay:500ms"` | `#job-list` |
| Filter Status | GET | `hx-trigger="change"` | `#job-list` |

## Security

- All dashboard/action views use `@login_required`
- Every query filters by `request.user` for data isolation
- CSRF tokens included in all HTMX forms
- `get_object_or_404` used for all single-object lookups
