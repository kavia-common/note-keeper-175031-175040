from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from .models import Note


class HealthTests(APITestCase):
    def test_health(self):
        url = reverse('Health')  # Make sure the URL is named
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Server is up!"})


class NoteCRUDTests(APITestCase):
    def setUp(self):
        # Create a few notes for list/retrieve tests
        self.note1 = Note.objects.create(title="Alpha", content="First", is_archived=False, tags="work,blue")
        self.note2 = Note.objects.create(title="Bravo", content="Second", is_archived=True, tags="home,amber")
        self.note3 = Note.objects.create(title="Charlie", content="Third", is_archived=False, tags="work")

    def test_create_note(self):
        url = "/api/notes/"
        payload = {"title": "New Note", "content": "hello", "is_archived": False, "tags": "misc"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", resp.data)
        self.assertIn("created_at", resp.data)
        self.assertIn("updated_at", resp.data)
        self.assertEqual(resp.data["title"], "New Note")

    def test_validation_error_empty_title(self):
        url = "/api/notes/"
        payload = {"title": "   ", "content": "x"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", resp.data)

    def test_list_with_pagination_and_filters(self):
        # request custom page_size, ensure capped by server reasonable default behavior (should allow page_size param)
        url = "/api/notes/?page=1&page_size=2"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # PageNumberPagination default structure
        self.assertIn("results", resp.data)
        self.assertLessEqual(len(resp.data["results"]), 2)

        # filter archived=true
        resp_arch = self.client.get("/api/notes/?archived=true")
        self.assertEqual(resp_arch.status_code, 200)
        self.assertTrue(all(item["is_archived"] is True for item in resp_arch.data["results"]))

        # filter archived=false
        resp_unarch = self.client.get("/api/notes/?archived=false")
        self.assertEqual(resp_unarch.status_code, 200)
        self.assertTrue(all(item["is_archived"] is False for item in resp_unarch.data["results"]))

        # search on title/content/tags
        resp_search = self.client.get("/api/notes/?search=work")
        self.assertEqual(resp_search.status_code, 200)
        self.assertTrue(all("work" in (item["tags"] or "").lower() or
                            "work" in (item["title"] or "").lower() or
                            "work" in (item["content"] or "").lower()
                            for item in resp_search.data["results"]))

    def test_retrieve_update_delete(self):
        # retrieve
        url_detail = f"/api/notes/{self.note1.id}/"
        resp = self.client.get(url_detail)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], self.note1.id)

        # full update (PUT)
        put_payload = {"title": "Alpha Updated", "content": "First+", "is_archived": True, "tags": "x,y"}
        resp_put = self.client.put(url_detail, put_payload, format="json")
        self.assertEqual(resp_put.status_code, 200)
        self.assertEqual(resp_put.data["title"], "Alpha Updated")
        self.assertTrue(resp_put.data["is_archived"])

        # partial update (PATCH)
        patch_payload = {"content": "Patched content"}
        resp_patch = self.client.patch(url_detail, patch_payload, format="json")
        self.assertEqual(resp_patch.status_code, 200)
        self.assertEqual(resp_patch.data["content"], "Patched content")

        # delete
        resp_del = self.client.delete(url_detail)
        self.assertEqual(resp_del.status_code, status.HTTP_204_NO_CONTENT)

        # fetch again -> 404
        resp_404 = self.client.get(url_detail)
        self.assertEqual(resp_404.status_code, status.HTTP_404_NOT_FOUND)

    def test_ordering(self):
        # ensure ordering by title ascending
        resp_title = self.client.get("/api/notes/?ordering=title&page_size=100")
        self.assertEqual(resp_title.status_code, 200)
        titles = [item["title"] for item in resp_title.data["results"]]
        self.assertEqual(titles, sorted(titles))

        # ensure ordering by -created_at default; also explicitly check
        resp_created_desc = self.client.get("/api/notes/?ordering=-created_at&page_size=100")
        self.assertEqual(resp_created_desc.status_code, 200)
        created_list = [item["created_at"] for item in resp_created_desc.data["results"]]
        self.assertEqual(created_list, sorted(created_list, reverse=True))
