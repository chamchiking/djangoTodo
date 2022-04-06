from django.db import models
from django.utils import timezone

# Create your models here.
class SoftDeletionManager(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField('삭제일', null=True, default=None)
    objects = SoftDeletionManager()

    class Meta:
        abstract = True # 상속할 수 있게

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])


class Todo(SoftDeletionModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='todos', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    desired_end_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_ended = models.BooleanField(null=True)

    class Meta:
        ordering=['created_at']

    def __str__(self):
        return self.title
    
    def was_published_in3days(self):
        now = timezone.now()
        return now - timezone.timedelta(days=3) <= self.desired_end_date <= now

class Tag(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='tags', on_delete=models.CASCADE)
    todos = models.ManyToManyField(Todo, related_name='tag_list', blank=True)
    name = models.CharField(max_length=50)
    text_color = models.CharField(max_length=50)
    background_color = models.CharField(max_length=50)

    class Meta:
        ordering=['created_at']

    def __str__(self):
        return self.name