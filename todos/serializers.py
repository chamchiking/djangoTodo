from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from djoser.serializers import UserCreatePasswordRetypeSerializer
from .models import Todo, Tag


class TagSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Tag
        fields='__all__'
        # fields=(
        #     'id',
        #     'owner',
        #     'created_at',
        #     'updated_at',
        #     'name',
        #     'text_color',
        #     'background_color',
        # )


class TodoSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # tag_list = TagSerializer(read_only=True,many=True, required=False)
    # tag_list = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     queryset = Tag.objects.all()
    # )
    tag_list = serializers.SlugRelatedField(
        many=True,
        queryset = Tag.objects.all(),
        slug_field='name'
    )
    class Meta:
        model = Todo
        fields=(
            'id',
            'owner',
            'tag_list',
            'created_at',
            'updated_at',
            'title',
            'description',
            'desired_end_date',
            'end_date',
            'is_ended',
        )
        read_only_fields = ('end_date',)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('email', 'id', 'username')

class UserWithTokenSerializer(UserCreatePasswordRetypeSerializer):
    auth_token = serializers.SerializerMethodField()
    class Meta:
        model=User
        fields=('email', 'username', 'password', 'auth_token')

    
    def get_auth_token(self, obj):
        return str(Token.objects.get_or_create(user=obj)[0])
            



class UserTodoTagSerializer(serializers.ModelSerializer):
    todos = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'
    )
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'todos',
            'tags',
            )