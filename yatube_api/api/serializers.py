import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from posts.models import Comment, Follow, Group, Post


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment


class FollowSerializer(serializers.ModelSerializer):

    following = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    user = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = ('user', 'following')
        model = Follow


'''    validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Подписка на себя невозможна.')
        return data'''
