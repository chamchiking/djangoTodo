from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from todos.models import Todo, Tag
from todos.serializers import TagSerializer, TodoSerializer

CREATE_USER_URL = 'http://localhost:8000/auth/users/'
TOKEN_URL = 'http://localhost:8000/auth/token/login/'
TAG_BASE_URL = reverse('tags-list')

def sample_tag(user, **params):
    defaults={
        'name': 'name',
        # 'text_color': '#25fa37',
        # 'background_color': '#25fa37'
    }
    defaults.update(params)
    return Tag.objects.create(owner=user, **defaults)


class PublicTagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAG_BASE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            username='testme',
            password='ckalscjf11'
        )
        self.client.force_authenticate(user = self.user)

    def test_retrieve_tags(self):
        # tag 제대로 받아오는지 테스트
        sample_tag(user=self.user)
        sample_tag(user=self.user)

        res = self.client.get(TAG_BASE_URL)

        tags = Tag.objects.all().order_by('created_at')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_tags_limited_to_user(self):
        # tag가 만든 유저에게만 보이는지 테스트
        user2 = get_user_model().objects.create_user(
            email='test2@test.com',
            username='testme2',
            password='ckalscjf11'
        )
        sample_tag(user=user2, name='first_tag')
        tag = sample_tag(user=self.user, name='second_tag')

        res = self.client.get(TAG_BASE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
    
    def test_create_tag_successful(self):
        payload={
            'name': 'Test Tag',
            # 'text_color': '#25fa37',
            # 'background_color': '#25fa37',
            }
        res = self.client.post(TAG_BASE_URL, payload)
        exists = Tag.objects.filter(
            owner=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_notdeletable_when_todo_exists(self):
        # 연결된 todo가 있는 경우 tag가 삭제 안됨
        tag1 = sample_tag(user=self.user)
        tags = Tag.objects.all()
        todo = Todo.objects.create(owner=self.user)
        todo.tag_list.set(tags)

        url = TAG_BASE_URL + str(tag1.id)+'/'
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieve_todos_connected_to_tag(self):
        # tag와 연결된 todo들 제대로 받아오는지 테스트
        tag = sample_tag(user=self.user)
        tags = Tag.objects.all()
        todo1 = Todo.objects.create(owner=self.user)
        todo2 = Todo.objects.create(owner=self.user)
        todo1.tag_list.set(tags)

        todo1 = TodoSerializer(todo1)
        todo2 = TodoSerializer(todo2)

        url = TAG_BASE_URL + str(tag.id) + '/todoList/'
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(todo1.data, res.data)
        self.assertNotIn(todo2.data, res.data)
