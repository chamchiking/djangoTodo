from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = 'http://localhost:8000/auth/users/'
TOKEN_URL = 'http://localhost:8000/auth/token/login/'
TODO_BASE_URL = 'http://localhost:8000/todos/'
# ME_URL = reverse('user:me')

from todos.models import Todo, Tag
from todos.serializers import TodoSerializer, TagSerializer
# from todos.views import *

def sample_todo(user, **params):
    defaults={
        'title': 'test',
        'description': '설명',
    }
    defaults.update(params)
    return Todo.objects.create(owner=user, **defaults)

def sample_tag(user, **params):
    defaults={
        'name': 'name',
        'text_color': 'text_color',
        'background_color': 'background_color'
    }
    defaults.update(params)
    return Tag.objects.create(owner=user, **defaults)

class PublicTodoTest(TestCase):
    def setUp(self):
        self.client = APIClient()
    def test_auth_required(self):
        res = self.client.get(TODO_BASE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTodoTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # 유저 한명 미리 생성
        self.user = get_user_model().objects.create_user(
            email = 'test@test.com',
            username =  'testme',
            password = 'ckalscjf11',
        )
        self.client.force_authenticate(user = self.user)
    

    def test_retrieve_todos(self):
        # todo 잘 받아오는지 확인
        sample_todo(user=self.user)
        sample_todo(user=self.user)

        res = self.client.get(TODO_BASE_URL)

        todos = Todo.objects.all().order_by('created_at')
        serializer = TodoSerializer(todos, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_todos_limited_to_user(self):
        # 유저에게 귀속된 todo만 받아오는지 확인
        user2 = get_user_model().objects.create_user(
            email = 'test2@test.com',
            username = 'testme2',
            password = 'ckalscjf11',
        )
        sample_todo(user=self.user)
        sample_todo(user=user2)

        res = self.client.get(TODO_BASE_URL)

        todos = Todo.objects.filter(owner=self.user).order_by('created_at')
        serializer = TodoSerializer(todos, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
    
    def test_create_todo(self):
        payload = {
            'title': 'new_todo',
            'description': 'description',
        }
        res = self.client.post(TODO_BASE_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        todo = Todo.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(todo, key))

    def test_create_todo_with_tags(self):
        # tag1 = sample_tag(user=self.user)
        # tag2 = sample_tag(user=self.user)
        # payload = {
        #     'title': 'todo with tags',
        #     'description': 'description about todo with tags',
        #     'tags': [tag1.id, tag2.id]
        # }
        # res = self.client.post(TODO_BASE_URL, payload)

        # self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # todo = Todo.objects.get(id=res.data['id'])
        # tags = todo.tags.all()
        # self.assertEqual(tags.count(), 2)
        # self.assertIn(tag1, tags)
        # self.assertIn(tag2, tags)
    

