from enum import IntEnum, Enum

from django.db import models


class PermissionFlag(IntEnum):
    EE = 1
    EW = 1 << 1
    ER = 1 << 2
    GE = 1 << 3
    GW = 1 << 4
    GR = 1 << 5
    OE = 1 << 6
    OW = 1 << 7
    OR = 1 << 8


class ButtonType(Enum):
    PRIMARY = 'primary'
    DISABLED_PRIMARY = 'primary disabled'
    SECONDARY = 'secondary'
    DISABLED_SECONDARY = 'secondary disabled'


class Parent(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Child(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    parents = models.ManyToManyField(Parent, related_name='+')
    text = models.TextField()
    int_number = models.IntegerField()
    uuid = models.UUIDField()
    url = models.URLField()
    description = models.TextField()
    config = models.JSONField()
    time = models.TimeField()
    slug = models.SlugField()
    ip_address = models.GenericIPAddressField()
    email = models.EmailField()
    bool_value = models.BooleanField()
    float_number = models.FloatField()
