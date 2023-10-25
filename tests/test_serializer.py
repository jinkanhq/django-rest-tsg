from django_rest_tsg import typescript
from tests.serializers import (
    ChildSerializer,
    ParentSerializer,
    PathSerializer,
    UserSerializer,
    DepartmentSerializer,
)


PATH_INTERFACE = """export interface Path {
  name: string;
  suffix: string;
  suffixes: string[];
  stem: string;
  isDirectory: boolean;
  size: number;
}"""

CHOICE_INTERFACE = """export interface Child {
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

USER_INTERFACE = """export interface User {
  primaryDepartment: Department;
  departments: Department[];
  dataPath: Path;
  id: number;
  name: string;
  profile: {[index: string]: any};
  birth: Date;
  lastLoggedIn: Date;
  followers: any[];
  status: 'active' | 'disabled';
  signature: string;
  publicKeys: string[];
  matrix: any[][];
  configs: {[index: string]: any}[];
  isStaff: boolean | null;
  eloRank: {[index: string]: number};
  magicNumber: 42;
  buttonType: ButtonType;
}"""

DEPARTMENT_INTERFACE = """export interface Department {
  id: number;
  name: string;
  permissions: string[];
  principals: User[];
}"""


def test_serializer():
    code = typescript.build_interface_from_serializer(PathSerializer)
    assert code.content == PATH_INTERFACE
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == PathSerializer


def test_model_serializer():
    code = typescript.build_interface_from_serializer(ChildSerializer)
    assert len(code.dependencies) == 1
    assert code.dependencies[0] == ParentSerializer
    assert code.content == CHOICE_INTERFACE
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == ChildSerializer


def test_dataclass_serializer():
    code = typescript.build_interface_from_serializer(UserSerializer)
    assert code.content == USER_INTERFACE
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == UserSerializer
    code = typescript.build_interface_from_serializer(DepartmentSerializer)
    assert code.content == DEPARTMENT_INTERFACE
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == DepartmentSerializer
