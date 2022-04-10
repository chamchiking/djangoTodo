import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse


from todos.models import Todo, Tag
from todos.serializers import TodoSerializer, TagSerializer

# from todos.views import *
CREATE_USER_URL = 'http://localhost:8000/auth/users/'
TOKEN_URL = 'http://localhost:8000/auth/token/login/'
TODO_BASE_URL = reverse('todos-list')

def sample_todo(user, **params):
    defaults={
        'title': 'test',
        'description': '설명',
        'desired_end_date': timezone.now(),
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
        # todo불러올때 authorization이 필요하다.
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
        # 기본 todo create test
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
        # tag가 달린 todo를 만드는 경우
        tag1 = sample_tag(user=self.user)
        tag2 = sample_tag(user=self.user, name='new name')
        payload = {
            'title': 'todo with tags',
            'description': 'description about todo with tags',
            'tag_list': [tag1.name, tag2.name],
        }
        res = self.client.post(TODO_BASE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        todo = Todo.objects.get(id=res.data['id'])
        tags = todo.tag_list.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_update_todo(self):
        todo = sample_todo(user=self.user)
        todo.tag_list.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='updated')

        payload = {
            'title': 'updated todo',
            'description': 'updated description',
            'tag_list': [new_tag.name]
        }
        url = TODO_BASE_URL + str(todo.id) + '/'
        self.client.put(url, payload)

        todo = Todo.objects.get(id=todo.id)
        self.assertEqual(todo.title, payload['title'])
        self.assertEqual(todo.description, payload['description'])
        tags = todo.tag_list.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_delete_todo(self):
        # delete 시 data가 안보이는지 확인
        todo = sample_todo(user=self.user)
        url = TODO_BASE_URL + str(todo.id) + '/'
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_retrieve_single_todo(self):
        # 하나의 todo data 받아오는거 확인
        todo = sample_todo(user=self.user)
        url = TODO_BASE_URL + str(todo.id) + '/'
        res = self.client.get(url)
        serializer = TodoSerializer(todo)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_within3day_todos(self):
        # 마감 3일 이내로 남은 todo 받아오는거 확인
        past_todo = sample_todo(user=self.user, desired_end_date=timezone.now()+timezone.timedelta(seconds=-1))
        future_todo = sample_todo(user=self.user, desired_end_date=timezone.now()+timezone.timedelta(days=3, seconds=1))
        in3days_todo = sample_todo(user=self.user, desired_end_date=timezone.now()+timezone.timedelta(days=3))
        url = TODO_BASE_URL + 'within3days/'
        res = self.client.get(url)
        past_todo = TodoSerializer(past_todo)
        future_todo = TodoSerializer(future_todo)
        in3days_todo = TodoSerializer(in3days_todo)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(past_todo.data, res.data)
        self.assertNotIn(future_todo.data, res.data)
        self.assertIn(in3days_todo.data, res.data)

    

