from django.contrib.auth.models import User
from django.utils import timezone
from django.http import Http404
import datetime
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Todo, Tag
from .permissions import IsOwner
from .serializers import TagSerializer, TodoSerializer, UserSerializer
from .filters import OwnerFilterBackend

# Create your views here.
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'todos': reverse('todo-list', request=request, format=format),
        'todos3daysleft': reverse('todo-3days-left', request=request, format=format),
        'tags': reverse('tag-list', request=request, format=format),
    })

class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    filter_backends = [OwnerFilterBackend]
    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
    def perform_update(self, serializer):
        if self.request.data.get('is_ended'):
            serializer.save(end_date=timezone.now())
        else:
            serializer.save()
# class TodoList(generics.ListCreateAPIView):
#     queryset = Todo.objects.all()
#     serializer_class = TodoSerializer
#     permission_classes = (permissions.IsAuthenticated,IsOwner )
#     filter_backends = [OwnerFilterBackend]

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

# class TodoDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Todo.objects.all()
#     serializer_class = TodoSerializer
#     permission_classes = (permissions.IsAuthenticated,IsOwner )
    
#     def perform_update(self, serializer):
#         if self.request.data.get('is_ended'):
#             serializer.save(end_date=timezone.now())
#         else:
#             serializer.save()

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    filter_backends = [OwnerFilterBackend]
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    def destroy(self, request, *args, **kwargs):
        try:
            tag = self.get_object()
            if not tag.todos.count():
                tag.delete()
            else:
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


# class TagList(generics.ListCreateAPIView):
#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer
#     permission_classes = (permissions.IsAuthenticated, )
#     filter_backends = [OwnerFilterBackend]

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

# class TagDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer
#     permission_classes = (permissions.IsAuthenticated,IsOwner)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             tag = self.get_object()
#             if not tag.todos.count():
#                 tag.delete()
#             else:
#                 return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         except Http404:
#             pass
#         return Response(status=status.HTTP_204_NO_CONTENT)



class TodoListByTag(generics.ListAPIView):
    serializer_class = TodoSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    filter_backends = [OwnerFilterBackend]
    
    def get_queryset(self):
        return Tag.objects.get(pk=self.kwargs['pk']).todos.all()


class Todo3DaysLeft(generics.ListAPIView):
    queryset = Todo.objects.filter(
        desired_end_date__range=(
            timezone.now(),
            timezone.now()+ datetime.timedelta(days=3)
            ))
    serializer_class = TodoSerializer
    permission_classes = (permissions.IsAuthenticated,IsOwner )
    filter_backends = [OwnerFilterBackend]


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer