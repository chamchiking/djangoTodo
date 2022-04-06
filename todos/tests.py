from django.test import TestCase
from .models import Todo, Tag
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from .views import *

# Create your tests here.
factory = APIRequestFactory()
user = User.objects.get(username='mincheol')
view = TodoDetail.as_view()
request = factory.get('todos/<int:pk>/')
force_authenticate(request, user=user)
response = view(request, pk=1)


# class TodoModelTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         Todo.objects.create(title='title',description='description')
    
#     def test_title_content(self):
#         todo = Todo.objects.get(id=1)
#         expected_object_name=f'{todo.title}'
#         self.assertEquals(expected_object_name, 'first todo')