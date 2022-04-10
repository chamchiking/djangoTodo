from django.urls import path, include
from rest_framework import routers
from todos import views

router = routers.DefaultRouter()
router.register(r'todos', views.TodoViewSet, basename='todos')
router.register(r'tags', views.TagViewSet, basename='tags')
router.register(r'users', views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('tags/<int:pk>/todoList/', views.TodoListByTag.as_view(), name='todo-list-by-tag'),
]