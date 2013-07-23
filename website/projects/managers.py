from operator import __or__ as OR
import random

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

from website.users.models import User


class ProjectQueryset(QuerySet):

    def filter_by_scope(self, scope=None):
        """Returns QS of all projects in a given scope."""
        return self.filter(countries__scope=scope).distinct()

    def get_random(self, max_number):
        """Returns a random QS with at most 'max_number' of elements"""
        length = self.count()
        if length <= max_number:
            return self
        else:
            random_indexes = random.sample(xrange(length), max_number)
            return [self[index] for index in random_indexes]


class ProjectManager(models.Manager):

    def get_query_set(self):
        return ProjectQueryset(self.model)

    def get_drafts_for_user(self, user):
        """Returns a queryset of drafts a user can edit"""
        drafts = self.filter(status=self.model.DRAFT)
        user_drafts = drafts.filter(
            Q(creator=user) | Q(collaborators__in=[user, ])
        ).distinct()
        return user_drafts

    def published(self):
        """Return QS of published projects"""
        return self.filter(status=self.model.PUBLISHED)

    def get_related_projects(self, user_or_package):
        """"Returns a queryset with all projects that are related."""
        active = self.filter(status=self.model.PUBLISHED)
        if isinstance(user_or_package, User):
            user = user_or_package
            projects = active.filter(collaborators__in=[user, ])
        else:
            package = user_or_package
            projects = active.filter(packages__in=[package, ])
        return projects

    def get_feature_projects(self):
        """Returns a queryset off all feature projects"""
        return self.filter(feature=True)

    def get_feature_project(self):
        """Returns a random feature project or None"""
        projects = self.get_feature_projects()
        project = random.choice(projects) if projects else None
        return project
