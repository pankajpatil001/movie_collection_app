from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from collection.models import Collection, Movie, RequestCounter

class RegistrationTestCase(APITestCase):
    def test_registration(self):
        data = {"username": "testuser", "password": "testpass"}
        response = self.client.post("/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('access_token' in response.json())

class LoginTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_login(self):
        data = {"username": "testuser", "password": "testpass"}
        response = self.client.post("/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access_token' in response.json())

class CollectionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.collection = Collection.objects.create(user=self.user, title="Test Collection", description="Test Description")

    def test_get_collections(self):
        response = self.client.get("/collection/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_collection(self):
        data = { "title": "my title 2", "description": "collection description", "movies": [] }
        response = self.client.post("/collection/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_collection_detail(self):
        response = self.client.get(reverse("rud_collection", kwargs={"collection_uuid": self.collection.uuid}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_collection(self):
        data = {"title": "Updated Collection", "description": "Updated Description", "movies": []}
        response = self.client.put(reverse("rud_collection", kwargs={"collection_uuid": self.collection.uuid}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_collection(self):
        response = self.client.delete(reverse("rud_collection", kwargs={"collection_uuid": self.collection.uuid}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class RequestCountTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)
        RequestCounter.objects.create(count=10)

    def test_get_request_count(self):
        response = self.client.get("/request-count/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['requests'], 11)

    def test_reset_request_count(self):
        response = self.client.post("/request-count/reset/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        counter = RequestCounter.objects.first()
        self.assertEqual(counter.count, 0)

class MoviesTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)
        
    def test_get_movies(self):
        response = self.client.get("/movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()['data']
        self.assertEqual(len(data), 10)