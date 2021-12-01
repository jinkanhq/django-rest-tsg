from enum import Enum, IntEnum

from django_rest_tsg import typescript


def test_int_enum():
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
    class ButtonType(Enum):
        PRIMARY = 'primary'
        DISABLED_PRIMARY = 'primary disabled'
        SECONDARY = 'secondary'
        DISABLED_SECONDARY = 'secondary disabled'

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
