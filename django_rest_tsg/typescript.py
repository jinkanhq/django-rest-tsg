from collections import ChainMap
from dataclasses import is_dataclass, fields, dataclass
from datetime import datetime, date
from enum import EnumMeta, IntEnum
from typing import get_origin, get_args, Annotated, Union, Any, Type, Dict, Optional, List, Tuple, Literal

from inflection import camelize
from rest_framework.serializers import (Serializer, BooleanField, CharField, ChoiceField, DateField,
                                        DateTimeField, DecimalField, DictField, EmailField, Field, FilePathField,
                                        FloatField, HStoreField, IPAddressField, IntegerField, ModelSerializer,
                                        ManyRelatedField, JSONField, ListField, ListSerializer, MultipleChoiceField,
                                        NullBooleanField, ReadOnlyField, RegexField, SerializerMethodField, SlugField,
                                        TimeField, URLField, UUIDField)
from rest_framework_dataclasses.fields import EnumField
from rest_framework_dataclasses.serializers import DataclassSerializer

from django_rest_tsg.templates import INTERFACE_TEMPLATE, INTERFACE_FIELD_TEMPLATE, ENUM_TEMPLATE, ENUM_MEMBER_TEMPLATE

LEFT_BRACKET = '['
RIGHT_BRACKET = ']'
UNION_SEPARATOR = ' | '

TYPESCRIPT_NULLABLE = '?'
TYPESCRIPT_ANY = 'any'
TYPESCRIPT_STRING = 'string'
TYPESCRIPT_NUMBER = 'number'
TYPESCRIPT_BOOLEAN = 'boolean'
TYPESCRIPT_DATE = 'Date'

GENERICS = (tuple, list, dict, Union, Literal)
GENERIC_FALLBACK_MAPPING = {
    list: 'any[]',
    tuple: 'any[]',
    dict: 'object',
}
TRIVIAL_TYPE_MAPPING: Dict[Type, str] = {
    int: TYPESCRIPT_NUMBER,
    float: TYPESCRIPT_NUMBER,
    str: TYPESCRIPT_STRING,
    bool: TYPESCRIPT_BOOLEAN,
    datetime: TYPESCRIPT_DATE,
    date: TYPESCRIPT_DATE,
    type(None): TYPESCRIPT_NULLABLE,
    Any: TYPESCRIPT_ANY,
}
DRF_FIELD_MAPPING: Dict[Type[Field], str] = {
    BooleanField: TYPESCRIPT_BOOLEAN,
    CharField: TYPESCRIPT_STRING,
    DateField: TYPESCRIPT_DATE,
    DateTimeField: TYPESCRIPT_DATE,
    DecimalField: TYPESCRIPT_STRING,
    EmailField: TYPESCRIPT_STRING,
    FilePathField: TYPESCRIPT_STRING,
    FloatField: TYPESCRIPT_NUMBER,
    HStoreField: "{[index: string]: string?}",
    IPAddressField: TYPESCRIPT_STRING,
    IntegerField: TYPESCRIPT_NUMBER,
    JSONField: TYPESCRIPT_ANY,
    MultipleChoiceField: TYPESCRIPT_ANY + '[]',
    NullBooleanField: TYPESCRIPT_BOOLEAN + TYPESCRIPT_NULLABLE,
    RegexField: TYPESCRIPT_STRING,
    ReadOnlyField: TYPESCRIPT_ANY,
    SerializerMethodField: TYPESCRIPT_ANY,
    SlugField: TYPESCRIPT_STRING,
    TimeField: TYPESCRIPT_STRING,
    URLField: TYPESCRIPT_STRING,
    UUIDField: TYPESCRIPT_STRING,
}
USER_DEFINED_TYPE_MAPPING: Dict[Type, str] = {}
TYPE_MAPPING = ChainMap(TRIVIAL_TYPE_MAPPING, USER_DEFINED_TYPE_MAPPING)
TYPE_MAPPING_WITH_GENERIC_FALLBACK = ChainMap(TRIVIAL_TYPE_MAPPING, USER_DEFINED_TYPE_MAPPING,
                                              GENERIC_FALLBACK_MAPPING)


class TypeScriptCodeType(IntEnum):
    INTERFACE = 0
    ENUM = 1


@dataclass
class TypeScriptCode:
    """
    TypeScript code snippet.
    """

    name: str
    type: TypeScriptCodeType
    source: Type[Any]
    content: str
    dependencies: List[Type]


def register(tp: Type, name: Optional[str] = None):
    """
    Register user-defined type.

    If no name is specified, use type name as default.
    """
    if name:
        USER_DEFINED_TYPE_MAPPING[tp] = name
    else:
        USER_DEFINED_TYPE_MAPPING[tp] = tp.__name__
    return tp


def tokenize_python_type(tp) -> list[Union[type, str]]:
    """
    Flatten a python type to a token list.

    Tokens can be of the following types:

    * Literals: 'foo', 42
    * Built-in types: list, dict
    * Types in typing module: Union, Literal
    * Brackets: '[' or ']'
    * User defined types
    """
    # non-generic fallback
    origin = get_origin(tp)
    if not origin:
        return [tp]

    current_type = tp
    result = []
    stack = []
    while True:
        if stack:
            top = stack.pop()
            if top == RIGHT_BRACKET:
                result.append(top)
                continue
            elif isinstance(top, str) or top in TYPE_MAPPING:
                result.append(top)
                current_type = top
                continue
            else:
                current_type = top
        origin = get_origin(current_type)
        if len(stack) == 0 and not origin:
            break
        if origin is Annotated:
            current_type = get_args(current_type)[0]
            continue
        elif origin in GENERICS:
            result.append(origin)
            result.append(LEFT_BRACKET)
            stack.append(RIGHT_BRACKET)
            args = get_args(current_type)
            for arg in reversed(args):
                stack.append(arg)
            print(current_type, args, stack)
        elif origin in TYPE_MAPPING:
            result.append(origin)
        # generic fallback
        elif current_type in (list, tuple):
            result += [current_type, LEFT_BRACKET, Any, RIGHT_BRACKET]
        elif current_type is dict:
            result.append('object')
    return result


def _build_type(tokens) -> str:
    """
    Build typescript type from tokens.
    """
    generic_stack: List = []
    children_stack: List[List] = []

    # fallback
    if len(tokens) == 1:
        tp = tokens[0]
        return TYPE_MAPPING_WITH_GENERIC_FALLBACK.get(tp, tp.__name__)

    for token in tokens:
        if token in GENERICS:
            generic_stack.append(token)
        elif token is LEFT_BRACKET:
            children_stack.append([])
        elif token is RIGHT_BRACKET:
            generic = generic_stack.pop()
            children = children_stack.pop()
            generic_children = []
            for child in children:
                if child not in generic_children:
                    generic_children.append(child)
            generic_type = _build_generic_type(generic, generic_children)
            if len(children_stack) > 0:
                children_stack[-1].append(generic_type)
            else:
                return generic_type
        else:
            children_stack[-1].append(TYPE_MAPPING.get(token, token))


def _build_generic_type(tp, children=None) -> str:
    """
    Build typescript type from python generic type with children.
    """
    if not children:
        children = []
    if tp is Union:
        if len(children) == 2 and TYPESCRIPT_NULLABLE in children:
            for child in children:
                if child == TYPESCRIPT_NULLABLE:
                    continue
                return ''.join((child, TYPESCRIPT_NULLABLE))
        return ' | '.join(children)
    elif tp in (list, tuple) and children:
        return f"Array<{children[0]}>"
    elif tp is dict and children:
        return f"{{[key: {children[0]}]: {children[1]}}}"
    elif tp is Literal:
        parts = []
        for child in children:
            if isinstance(child, str):
                part = f"'{child}'"
            else:
                part = child
            parts.append(part)
        return ' | '.join(parts)


def build_type(tp) -> Tuple[str, List[Type]]:
    """
    Build typescript type from python type.
    """
    tokens = tokenize_python_type(tp)
    dependencies = [token for token in tokens if token not in TYPE_MAPPING_WITH_GENERIC_FALLBACK]
    return _build_type(tokens), dependencies


def build_enum(enum_tp: EnumMeta, enum_name: str = None, enforce_uppercase: bool = False) -> TypeScriptCode:
    """
    Build typescript enum from python enum.
    """
    enum_members = []
    for name, member in enum_tp.__members__.items():
        member_type = type(member.value)
        member_value = member.value
        if member_type is str:
            member_value = f"'{member.value}'"
        if enforce_uppercase:
            member_name = name.upper()
        else:
            member_name = camelize(name.lower(), uppercase_first_letter=False)
            member_name = member_name[0].upper() + member_name[1:]
        enum_members.append(ENUM_MEMBER_TEMPLATE.substitute(name=member_name, value=member_value))
    if not enum_name:
        enum_name = enum_tp.__name__
    return TypeScriptCode(type=TypeScriptCodeType.ENUM, source=enum_tp, name=enum_name, dependencies=[],
                          content=ENUM_TEMPLATE.substitute(members=',\n'.join(enum_members), name=enum_tp.__name__))


def build_interface_from_dataclass(data_cls) -> TypeScriptCode:
    """
    Build typescript interface from python dataclass.
    """
    assert is_dataclass(data_cls)
    interface_fields = []
    interface_dependencies = set()
    for field in fields(data_cls):
        field_type_representation, field_dependencies = build_type(field.type)
        interface_dependencies |= set(field_dependencies)
        interface_fields.append(
            INTERFACE_FIELD_TEMPLATE.substitute(name=camelize(field.name, uppercase_first_letter=False),
                                                type=field_type_representation))
    return TypeScriptCode(type=TypeScriptCodeType.INTERFACE, source=data_cls, name=data_cls.__name__,
                          dependencies=list(interface_dependencies),
                          content=INTERFACE_TEMPLATE.substitute(fields='\n'.join(interface_fields),
                                                                name=data_cls.__name__))


def get_serializer_prefix(serializer_class: Type[Serializer]):
    """FooSerializer -> Foo"""
    return serializer_class.__name__[:-10]


def _get_serializer_field_type(field: Field) -> Tuple[str, Optional[Type]]:
    """
    Get typescript type from trivial serializer field.
    """
    field_type: str
    dependency = None
    if type(field) in DRF_FIELD_MAPPING:
        field_type = DRF_FIELD_MAPPING[type(field)]
    elif isinstance(field, ModelSerializer):
        field_type = field.Meta.model.__name__
    elif isinstance(field, DataclassSerializer):
        field_type = field.Meta.dataclass.__name__
    elif isinstance(field, EnumField):
        field_type = field.enum_class.__name__
        dependency = field.enum_class
    elif isinstance(field, ChoiceField):
        parts = []
        for value in field.choices.values():
            if isinstance(value, str):
                part = f"'{value}'"
            else:
                part = value
            parts.append(part)
        field_type = ' | '.join(parts)
    elif isinstance(field, ManyRelatedField):
        raise Exception('No explicit type hinting.')
    elif isinstance(field, ListSerializer):
        field_type = get_serializer_prefix(type(field.child)) + "[]"
        dependency = type(field.child)
    elif isinstance(field, Serializer):
        field_type = get_serializer_prefix(type(field))
        dependency = field
    return field_type, dependency


def get_serializer_field_type(field: Field) -> Tuple[str, list]:
    """
    Get typescript type from serializer field

    Composite fields will be flattened.
    """
    stack = []
    result = ''
    dependencies = set()
    while True:
        if isinstance(field, (DictField, ListField)):
            stack.append(type(field))
            field = field.child
        else:
            field_type, field_dependency = _get_serializer_field_type(field)
            if field_dependency:
                dependencies.add(field_dependency)
            stack.append(field_type)
            break
    for item in reversed(stack):
        if item is ListField:
            result += '[]'
        elif item is DictField:
            result = f'{{[index: string]: {result}}}'
        else:
            result = item
    return result, sorted(list(dependencies))


def build_interface_from_serializer(serializer_class: Type[Serializer],
                                    interface_name: Optional[str] = None) -> TypeScriptCode:
    """
    Build typescript interface from django rest framework serializer.
    """
    assert issubclass(serializer_class, Serializer)
    serializer: Serializer = serializer_class()
    interface_fields = []
    interface_dependencies = set()
    for field_name, field_instance in serializer.get_fields().items():
        field_type = type(field_instance)
        if field_type in DRF_FIELD_MAPPING:
            field_type = DRF_FIELD_MAPPING[field_type]
        else:
            field_type, field_dependencies = get_serializer_field_type(field_instance)
            for dependency in field_dependencies:
                interface_dependencies.add(dependency)
        interface_fields.append(
            INTERFACE_FIELD_TEMPLATE.substitute(name=camelize(field_name, uppercase_first_letter=False),
                                                type=field_type))

    if not interface_name:
        interface_name = get_serializer_prefix(serializer_class)
    return TypeScriptCode(type=TypeScriptCodeType.INTERFACE, source=serializer_class, name=interface_name,
                          dependencies=sorted(list(interface_dependencies)),
                          content=INTERFACE_TEMPLATE.substitute(fields='\n'.join(interface_fields),
                                                                name=interface_name))
