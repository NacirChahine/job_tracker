# AI Project Docs — Job Tracker

## Architecture

**Pattern:** Django Function-Based Views + HTMX partial rendering ("HTML over the wire").

All views return full page renders for direct browser navigation, but HTMX requests receive only the relevant HTML fragment (partial template). No REST API, no JSON serialization — pure Django template rendering.

## Data Model

### JobApplication

| Field | Type | Notes |
|-------|------|-------|
| user | FK → auth.User | CASCADE, data isolation |
| company_name | CharField(255) | |
| position | CharField(255) | |
| status | CharField(20) | Choices: Applied, Interview, Offer, Rejected |
| applied_date | DateField | default=timezone.now |
| link | URLField | blank=True |
| notes | TextField | blank=True |
| created_at | DateTimeField | auto_now_add |
| updated_at | DateTimeField | auto_now |

Meta ordering: `-created_at`

## View Reference

### Auth Views (no login required)
- `register_view` — POST: create user + login; GET: registration form
- `login_view` — POST: authenticate + redirect; GET: login form
- `logout_view` — logout + redirect to login

### Dashboard (login required)
- `dashboard` — Full page render with applications list + create form

### HTMX Partials (login required)
- `job_list` — GET: filtered/searched job list fragment
- `job_create` — POST: create job, return job_item partial
- `job_detail` — GET: single job_item partial
- `job_edit_form` — GET: edit form partial (replaces job_item)
- `job_update` — POST/PUT/PATCH: save edit, return job_item partial
- `job_status_update` — POST/PATCH: update status, return job_item partial
- `job_notes_edit` — GET: notes editor partial; POST/PUT: save notes, return notes_display partial
- `job_delete` — DELETE: remove job, return 200

## URL Patterns

All under app_name `tracker`:

| URL | View | Name |
|-----|------|------|
| `/` | dashboard | dashboard |
| `/jobs/` | job_list | job_list |
| `/jobs/create/` | job_create | job_create |
| `/jobs/<pk>/` | job_detail | job_detail |
| `/jobs/<pk>/edit/` | job_edit_form | job_edit_form |
| `/jobs/<pk>/update/` | job_update | job_update |
| `/jobs/<pk>/status/` | job_status_update | job_status_update |
| `/jobs/<pk>/notes/` | job_notes_edit | job_notes_edit |
| `/jobs/<pk>/delete/` | job_delete | job_delete |
| `/login/` | login_view | login |
| `/logout/` | logout_view | logout |
| `/register/` | register_view | register |

## Forms

- `JobApplicationForm` — Creation form (all fields except user)
- `JobApplicationEditForm` — Edit form (all fields except user)
- `StatusUpdateForm` — Status-only update
- `NotesEditForm` — Notes-only update
- `RegistrationForm` — Custom registration with password confirmation

## Template Hierarchy

- `base.html` — Bootstrap 5 + HTMX 2.x CDN, navbar, form reset script
- `dashboard.html` — Two-column layout: add form + job list with search/filter
- `partials/job_list.html` — Loop over applications, includes job_item
- `partials/job_item.html` — Single card with status badge, dropdown, edit/delete buttons, notes
- `partials/job_form.html` — Shared form for create (id=job-form, hx-post to create, swap afterbegin) and edit (id=edit-form-{{ job.id }}, wrapped in div#job-{{ job.id }}, hx-post to update, swap outerHTML)
- `partials/notes_edit.html` — Inline textarea for notes editing, wrapped in div#notes-{{ job.id }}, targets #notes-{{ job.id }} with outerHTML swap
- `partials/notes_display.html` — Notes display section (reused by job_item and notes_edit success response)
- `registration/login.html` — Login form
- `registration/register.html` — Registration form

## Key Design Decisions

1. **FBV over CBV:** Cleaner HTMX partial returns, explicit control flow
2. **No DRF:** Pure template rendering, no JSON API layer
3. **HTMX 2.x:** Form reset only on successful create via `htmx:afterRequest` + `event.detail.successful` check
4. **CSRF on DELETE:** Delete button wrapped in `<form>` with `{% csrf_token %}` so HTMX DELETE includes CSRF token
5. **Edit form container:** Edit form wrapped in `div#job-{{ job.id }}` so `hx-target` always resolves correctly for Save and Cancel
6. **Notes scoped swap:** Notes edit targets `#notes-{{ job.id }}` with outerHTML, returns `notes_display.html` on success (not full card)
7. **Status dropdown auto-submit:** `onchange` dispatches submit event on parent form
8. **Delete animation:** `hx-swap="outerHTML swap:0.3s"` with CSS transition on `.htmx-swapping`
9. **Search debouncing:** `hx-trigger="keyup changed delay:500ms"` prevents excessive requests
