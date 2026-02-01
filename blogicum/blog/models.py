from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .constants import MAX_CHARFIELD_LENGTH, PREVIEW_TEXT_LENGTH

User = get_user_model()


class PublishCreated(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class Category(PublishCreated):
    title = models.CharField(
        'Заголовок',
        max_length=MAX_CHARFIELD_LENGTH,
    )
    description = models.TextField('Описание', )
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; разрешены '
        'символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:PREVIEW_TEXT_LENGTH]


class Location(PublishCreated):
    name = models.CharField('Название места', max_length=MAX_CHARFIELD_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:PREVIEW_TEXT_LENGTH]


class Post(PublishCreated):
    title = models.CharField(
        'Заголовок',
        max_length=MAX_CHARFIELD_LENGTH,
    )
    text = models.TextField('Текст', )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.'
    )
    image = models.ImageField('Фото', blank=True, upload_to='images')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title[:PREVIEW_TEXT_LENGTH]
    

class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta:
        ordering = ('-created_at',)
