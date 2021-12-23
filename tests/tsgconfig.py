from django_rest_tsg.build import build
from tests.models import PermissionFlag, User
from tests.serializers import PathSerializer, ChildSerializer

BUILD_TASKS = [
    build(PathSerializer),
    build(ChildSerializer, alias="FoobarChild"),
    build(PermissionFlag),
    build(User),
]
