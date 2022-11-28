# TODO:  Напишите свой вариант
from django.shortcuts import get_object_or_404
from posts.models import Comment, Follow, Group, Post, User
from rest_framework import filters, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination

from .serializers import CommentSerializer, FollowSerializer
from .serializers import GroupSerializer, PostSerializer

from rest_framework import status
from rest_framework.response import Response


class PostViewSet(viewsets.ModelViewSet):

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        return super().perform_destroy(instance)

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.author:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        return super().perform_update(serializer)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        comments_queryset = Comment.objects.filter(post_id=post_id)
        return comments_queryset

    def perform_create(self, serializer):
        get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user,
                        post_id=self.kwargs.get('post_id'))

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Измение чужого контента запрещено!')
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        return super().perform_destroy(instance)


class FollowViewSet(viewsets.ModelViewSet):

    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^following__username',)

    def get_queryset(self):
        follows_queryset = Follow.objects.filter(user=self.request.user)
        return follows_queryset

    def create(self, request):
        print(request.data)
        author = User.objects.get(username=self.request.data.get('following'))
        follow = Follow.objects.get_or_create(user=self.request.user,
                                              following=author)
        serializer = self.serializer_class(data=follow)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,  status=status.HTTP_400_BAD_REQUEST)


'''    def perform_create(self, serializer):
        serializer.save(user=self.request.user)'''
