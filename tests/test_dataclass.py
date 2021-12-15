from django_rest_tsg import typescript
from tests.models import User, Department


def test_dataclass():
    typescript.register(Department, 'Department')

    user_interface = """export interface User {
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
  isStaff: boolean?;
  eloRank: {[key: string]: number};
  magicNumber: 42;
  buttonType: ButtonType;
}"""
    code = typescript.build_interface_from_dataclass(User)
    assert code.content == user_interface
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == User

    department_interface = """export interface Department {
  id: number;
  name: string;
  permissions: Array<string>;
  principals: Array<User | number>;
}"""
    code = typescript.build_interface_from_dataclass(Department)
    assert code.content == department_interface
    assert code.type == typescript.TypeScriptCodeType.INTERFACE
    assert code.source == Department
