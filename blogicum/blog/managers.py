from django.db import models
from django.db.models import Count
from django.utils import timezone


class PublishedPostQuerySet(models.QuerySet['Post']):
    def published(self):
        return self.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    def with_comment_count(self):
        return self.annotate(comment_count=Count("comments"))

    def with_related(self):
        return self.select_related("author", "location", "category")

    def published_with_comments(self):
        return self.published().with_comment_count()
