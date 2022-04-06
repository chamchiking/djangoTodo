from django.contrib.auth.models import User
from rest_framework import serializers
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
    tag_list = TagSerializer(read_only=True, many=True)
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