from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Union, Literal

from django_rest_tsg import typescript


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


@typescript.register
@dataclass
class Department:
    id: int
    name: str
    permissions: List[str]
    principals: List[Union[User, int]]


def test_dataclass():
    user_interface = """export interface User {
  id: number;
  name: string;
  profile: object;
  birth: Date;
  lastLoggedIn: Date;
  followers: any[];
  status: 'active' | 'disabled';
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
