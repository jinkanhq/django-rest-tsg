from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from tests.models import Parent, Child, User, Department


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = "__all__"


class ChildSerializer(serializers.ModelSerializer):
    parent = ParentSerializer()
    parents = ParentSerializer(many=True)

    class Meta:
        model = Child
        fields = "__all__"


class PathSerializer(serializers.Serializer):
    name = serializers.CharField()
    suffix = serializers.CharField()
    suffixes = serializers.ListField(child=serializers.CharField())
    stem = serializers.CharField()
    is_directory = serializers.BooleanField(source="is_dir")
    size = serializers.IntegerField(source="stat.st_size")


class PathWrapperSerializer(serializers.Serializer):
    path = PathSerializer()
    meta = serializers.JSONField()


class DepartmentSerializer(DataclassSerializer):
    class Meta:
        dataclass = Department


class UserSerializer(DataclassSerializer):
    primary_department = DepartmentSerializer()
    departments = DepartmentSerializer(many=True)
    data_path = PathSerializer()

    class Meta:
        dataclass = User
