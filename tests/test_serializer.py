from django_rest_tsg import typescript
from tests.serializers import ChildSerializer, ParentSerializer, PathSerializer


def test_serializer():
    path_interface = """export interface Path {
  name: string;
  suffix: string;
  suffixes: string[];
  stem: string;
  isDirectory: boolean;
  size: number;
}"""
    code = typescript.build_interface_from_serializer(PathSerializer)
    assert code.content == path_interface
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == PathSerializer


def test_model_serializer():
    choice_interface = """export interface Child {
  id: number;
  parent: Parent;
  parents: Parent[];
  text: string;
  intNumber: number;
  uuid: string;
  url: string;
  description: string;
  config: any;
  time: string;
  slug: string;
  ipAddress: string;
  email: string;
  boolValue: boolean;
  floatNumber: number;
}"""

    code = typescript.build_interface_from_serializer(ChildSerializer)
    assert len(code.dependencies) == 1
    assert code.dependencies[0] == ParentSerializer
    assert code.content == choice_interface
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == ChildSerializer
