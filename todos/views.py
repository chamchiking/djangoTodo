from django.contrib.auth.models import User
from django.utils import timezone
from django.http import Http404
import datetime
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Todo, Tag
from .permissions import IsOwner
from .serializers import TagSerializer, TodoSerializer, UserTodoTagSerializer
from .filters import OwnerFilterBackend


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserTodoTagSerializer

class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    filter_backends = [OwnerFilterBackend]

    @action(detail=False)
    def within3days(self, request):
        queryset = Todo.objects.filter(
            desired_end_date__range=(
                timezone.now(),
                timezone.now()+ datetime.timedelta(days=3)
                ))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
    def perform_update(self, serializer):
        if self.request.data.get('is_ended'):
            serializer.save(end_date=timezone.now())
        else:
            serializer.save()

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


class TodoListByTag(generics.ListAPIView):
    serializer_class = TodoSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    filter_backends = [OwnerFilterBackend]
    
    def get_queryset(self):
        return Tag.objects.get(pk=self.kwargs['pk']).todos.all()



# class UserList(generics.ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserTodoTagSerializer

# class UserDetail(generics.RetrieveAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserTodoTagSerializer