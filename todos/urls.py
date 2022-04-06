from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from todos import views

urlpatterns = [
    path('todos/', views.TodoList.as_view(), name='todo-list'),
    path('todos/<int:pk>/', views.TodoDetail.as_view(), name='todo-detail'),
    path('todos/3daysleft/', views.Todo3DaysLeft.as_view(), name='todo-3days-left'),
    path('tags/', views.TagList.as_view(), name='tag-list'),
    path('tags/<int:pk>/', views.TagDetail.as_view(), name='tag-detail'),
    path('tags/<int:pk>/todoList', views.TodoListByTag.as_view(), name='todo-list-by-tag'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('', views.api_root),
]

urlpatterns = format_suffix_patterns(urlpatterns)