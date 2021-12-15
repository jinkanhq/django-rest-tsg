from dataclasses import dataclass
from datetime import date, datetime
from enum import IntEnum, Enum
from typing import Literal, Annotated, List, Optional, Dict, Union

from django.db import models

from django_rest_tsg import typescript


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


@typescript.register
@dataclass
class User:
    id: int
    name: str
    profile: dict
    birth: date
    last_logged_in: datetime
    followers: list
    status: Literal['active', 'disabled']
    signature: Annotated[str, 'Something I can\'t explain']
    public_keys: Annotated[List[str], 'SSH Keys']
    matrix: List[list]
    configs: List[dict]
    is_staff: Optional[bool]
    elo_rank: Dict[str, float]
    magic_number: Literal[42]
    button_type: ButtonType


@dataclass
class Department:
    id: int
    name: str
    permissions: List[str]
    principals: List[Union[User, int]]
