from django_rest_tsg import typescript
from tests.models import PermissionFlag, ButtonType


def test_int_enum():
    permission_flag = """export enum PermissionFlag {
  EE = 1,
  EW = 2,
  ER = 4,
  GE = 8,
  GW = 16,
  GR = 32,
  OE = 64,
  OW = 128,
  OR = 256
}"""
    code = typescript.build_enum(PermissionFlag, enforce_uppercase=True)
    assert code.content == permission_flag
    assert code.type == typescript.TypeScriptCodeType.ENUM
    assert code.source == PermissionFlag


def test_str_enum():
    button_type = """export enum ButtonType {
  Primary = 'primary',
  DisabledPrimary = 'primary disabled',
  Secondary = 'secondary',
  DisabledSecondary = 'secondary disabled'
}"""
    code = typescript.build_enum(ButtonType)
    assert code.content == button_type
    assert code.type == typescript.TypeScriptCodeType.ENUM
    assert code.source == ButtonType
