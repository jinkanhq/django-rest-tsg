from django_rest_tsg import typescript
from tests.models import User, Department, UserList


USER_INTERFACE = """export interface User {
  id: number;
  name: string;
  profile: object;
  birth: Date;
  lastLoggedIn: Date;
  followers: any[];
  status: 'active' | 'disabled';
  signature: string;
  publicKeys: Array<string>;
  matrix: Array<Array<any>>;
  configs: Array<object>;
  isStaff: boolean | null;
  eloRank: {[key: string]: number};
  magicNumber: 42;
  buttonType: ButtonType;
}"""


def test_dataclass():
    typescript.register(Department, "Department")
    code = typescript.build_interface_from_dataclass(User)
    assert code.content == USER_INTERFACE
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == User

    department_interface = """export interface Department {
  id: number;
  name: string;
  permissions: Array<string>;
  principals: Array<User>;
}"""
    code = typescript.build_interface_from_dataclass(Department)
    assert code.content == department_interface
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == Department

    user_list_interface = """export interface UserList {
  id: number;
  users: Array<User | number | string>;
}"""
    code = typescript.build_interface_from_dataclass(UserList)
    assert code.content == user_list_interface
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == UserList
