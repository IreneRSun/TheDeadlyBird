from rest_framework import serializers
from identity.serializers import AuthorSerializer
from .models import Post, PostCategoryMeta, Comment

class PostSerializer(serializers.ModelSerializer):
  type = serializers.ReadOnlyField(default="post")
  contentType = serializers.CharField(source="content_type")
  author = serializers.SerializerMethodField()
  categories = serializers.SerializerMethodField()
  count = serializers.SerializerMethodField()
  comments = serializers.SerializerMethodField()
  commentsSrc = serializers.SerializerMethodField()
  published = serializers.DateTimeField(source="published_date")

  def get_author(self, object: Post):
    return AuthorSerializer(object.author).data

  def get_categories(self, object: Post):
    categories = list(map(lambda c: c.category, list(PostCategoryMeta.objects.all().filter(post=object))))
    return categories

  def get_count(self, object: Post):
    return Comment.objects.filter(post=object).count()
  
  def get_comments(self, object: Post):
    # TODO: URL to comments
    return ""
  
  def get_commentsSrc(self, object: Post):
    # TODO: 5 comments sorted newest to oldest in the api spec format
    return {
      'type': 'comments',
      'page': 1,
      'size': 5,
      'post': '',  # TODO: URL to post?
      'id': '', # TODO: ??? Comments page id?...
      'comments': []  # TODO: Get and serialize comments
    }

  class Meta:
    model = Post
    fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'categories', 'count', 'comments', 'commentsSrc', 'published', 'visibility']