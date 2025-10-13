from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import JobApplication


class JobApplicationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "password123")

    def test_create_job(self):
        job = JobApplication.objects.create(
            user=self.user, company_name="Google", position="SWE", status="Applied"
        )
        self.assertEqual(str(job), "SWE at Google")
        self.assertEqual(job.status, "Applied")
        self.assertIsNotNone(job.applied_date)

    def test_ordering(self):
        import datetime
        from django.utils import timezone
        j1 = JobApplication.objects.create(user=self.user, company_name="Alpha", position="First")
        j2 = JobApplication.objects.create(user=self.user, company_name="Beta", position="Second")
        JobApplication.objects.filter(pk=j1.pk).update(
            created_at=timezone.now() - datetime.timedelta(hours=1)
        )
        jobs = list(JobApplication.objects.filter(user=self.user))
        self.assertEqual(jobs[0].company_name, "Beta")
        self.assertEqual(jobs[1].company_name, "Alpha")

    def test_status_choices(self):
        valid = {c[0] for c in JobApplication.STATUS_CHOICES}
        self.assertEqual(valid, {"Applied", "Interview", "Offer", "Rejected"})


class AuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@test.com", "password123")

    def test_login_page_renders(self):
        r = self.client.get("/login/")
        self.assertEqual(r.status_code, 200)

    def test_register_page_renders(self):
        r = self.client.get("/register/")
        self.assertEqual(r.status_code, 200)

    def test_register_user(self):
        r = self.client.post("/register/", {
            "username": "newuser",
            "email": "new@test.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_user(self):
        r = self.client.post("/login/", {"username": "testuser", "password": "password123"})
        self.assertEqual(r.status_code, 302)

    def test_logout(self):
        self.client.login(username="testuser", password="password123")
        r = self.client.get("/logout/")
        self.assertEqual(r.status_code, 302)

    def test_dashboard_requires_login(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r.url)


class DataIsolationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user("user1", "u1@test.com", "pass123")
        self.user2 = User.objects.create_user("user2", "u2@test.com", "pass123")
        self.job1 = JobApplication.objects.create(
            user=self.user1, company_name="Google", position="SWE"
        )
        self.job2 = JobApplication.objects.create(
            user=self.user2, company_name="Meta", position="MLE"
        )

    def test_user1_cannot_see_user2_jobs(self):
        self.client.login(username="user1", password="pass123")
        r = self.client.get("/jobs/")
        self.assertContains(r, "Google")
        self.assertNotContains(r, "Meta")

    def test_user2_cannot_see_user1_jobs(self):
        self.client.login(username="user2", password="pass123")
        r = self.client.get("/jobs/")
        self.assertContains(r, "Meta")
        self.assertNotContains(r, "Google")

    def test_user_cannot_delete_other_user_job(self):
        self.client.login(username="user2", password="pass123")
        r = self.client.delete(f"/jobs/{self.job1.id}/delete/")
        self.assertEqual(r.status_code, 404)
        self.assertTrue(JobApplication.objects.filter(pk=self.job1.id).exists())

    def test_user_cannot_edit_other_user_job(self):
        self.client.login(username="user2", password="pass123")
        r = self.client.get(f"/jobs/{self.job1.id}/edit/")
        self.assertEqual(r.status_code, 404)


class HTMXPartialTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@test.com", "password123")
        self.client.login(username="testuser", password="password123")

    def test_dashboard_renders(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Add Application")

    def test_create_job_partial(self):
        r = self.client.post("/jobs/create/", {
            "company_name": "Apple",
            "position": "iOS Dev",
            "status": "Applied",
            "applied_date": "2026-04-22",
            "link": "",
            "notes": "",
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Apple")
        self.assertContains(r, "iOS Dev")

    def test_job_list_partial(self):
        JobApplication.objects.create(user=self.user, company_name="Netflix", position="Backend")
        r = self.client.get("/jobs/")
        self.assertContains(r, "Netflix")

    def test_search_filter(self):
        JobApplication.objects.create(user=self.user, company_name="Amazon", position="SDE")
        JobApplication.objects.create(user=self.user, company_name="Stripe", position="API Eng")
        r = self.client.get("/jobs/", {"search": "Amazon"})
        self.assertContains(r, "Amazon")
        self.assertNotContains(r, "Stripe")

    def test_status_filter(self):
        JobApplication.objects.create(user=self.user, company_name="AcmeCorp", position="Dev", status="Applied")
        JobApplication.objects.create(user=self.user, company_name="ZenithInc", position="Eng", status="Offer")
        r = self.client.get("/jobs/", {"status": "Offer"})
        self.assertContains(r, "ZenithInc")
        self.assertNotContains(r, "AcmeCorp")

    def test_status_update(self):
        job = JobApplication.objects.create(user=self.user, company_name="X", position="Y", status="Applied")
        r = self.client.post(f"/jobs/{job.id}/status/", {"status": "Interview"})
        self.assertEqual(r.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.status, "Interview")

    def test_notes_edit_get(self):
        job = JobApplication.objects.create(user=self.user, company_name="X", position="Y")
        r = self.client.get(f"/jobs/{job.id}/notes/")
        self.assertEqual(r.status_code, 200)

    def test_notes_edit_post(self):
        job = JobApplication.objects.create(user=self.user, company_name="X", position="Y")
        r = self.client.post(f"/jobs/{job.id}/notes/", {"notes": "Updated notes"})
        self.assertEqual(r.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.notes, "Updated notes")

    def test_delete_job(self):
        job = JobApplication.objects.create(user=self.user, company_name="X", position="Y")
        r = self.client.delete(f"/jobs/{job.id}/delete/")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(JobApplication.objects.filter(pk=job.id).exists())

    def test_edit_form_get(self):
        job = JobApplication.objects.create(user=self.user, company_name="X", position="Y")
        r = self.client.get(f"/jobs/{job.id}/edit/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Save Changes")

    def test_update_job(self):
        job = JobApplication.objects.create(user=self.user, company_name="X", position="Y")
        r = self.client.post(f"/jobs/{job.id}/update/", {
            "company_name": "Updated",
            "position": "NewPos",
            "status": "Interview",
            "applied_date": "2026-04-22",
            "link": "",
            "notes": "",
        })
        self.assertEqual(r.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.company_name, "Updated")
