from django.urls import path, include
from rest_framework import routers
from todos import views

router = routers.DefaultRouter()
router.register(r'todos', views.TodoViewSet, basename='todos')
router.register(r'tags', views.TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('todos/3daysleft/', views.Todo3DaysLeft.as_view(), name='todo-3days-left'),
    path('tags/<int:pk>/todoList', views.TodoListByTag.as_view(), name='todo-list-by-tag'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    # path('', views.api_root),
]