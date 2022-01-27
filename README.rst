.. image:: https://github.com/jinkanhq/django-rest-tsg/actions/workflows/coverage.yml/badge.svg
    :target: https://github.com/jinkanhq/django-rest-tsg/actions/workflows/coverage.yml

.. image:: https://codecov.io/gh/jinkanhq/django-rest-tsg/branch/main/graph/badge.svg?token=LX8E3QB541
    :target: https://codecov.io/gh/jinkanhq/django-rest-tsg

.. image:: https://badge.fury.io/py/django-rest-tsg.svg
    :target: https://badge.fury.io/py/django-rest-tsg

django-rest-tsg
====================

A TypeScript code generator for Django Rest Framework, which saved your hand-working and guaranteed consistency
between Python codes and modern frontend codes written in TypeScript.

Features
----------

It generates TypeScript codes from following Python types.

* Django REST Framework serializers: manual working on ``Serializer``, ``ModelSerializer``
  derived from Django ORM models, ``DataclassSerializer`` via `djangorestframework-dataclasses`_
* Python dataclasses: Classes decorated by ``dataclasses.dataclass``.
* Python enums: Subclasses of ``enum.Enum``.

It also supports nested types and composite types.

.. _djangorestframework-dataclasses: https://github.com/oxan/djangorestframework-dataclasses

Requirements
--------------

* Python >3.9
* Django >3.0
* Django REST Framework >3.12

Usage
--------

Install using ``pip``

.. code-block:: bash

  $ pip install django_rest_tsg

Put a ``tsgconfig.py`` file with build tasks into your django project's root.

.. code-block:: python

    from django.conf import settings
    from django_rest_tsg.build import build

    BUILD_DIR = settings.BASE_DIR / "app/src/core"

    BUILD_TASKS = [
        build(Foo),
        build(BarSerializer, {"alias": "Foobar"}),
    ]

Add ``django_rest_tsg`` to your ``INSTALLED_APPS``.

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "django_rest_tsg"
    ]

Run ``buildtypescript`` command on ``manage.py``.

.. code-block:: bash

    $ python manage.py buildtypescript

Or you can switch to another place.

.. code-block:: bash

    $ python manage.py buildtypescript --build-dir /somewhere/you/cannot/explain

Examples
-----------------

Input: Serializer

.. code-block:: python

    class PathSerializer(serializers.Serializer):
        name = serializers.CharField()
        suffix = serializers.CharField()
        suffixes = serializers.ListField(child=serializers.CharField())
        stem = serializers.CharField()
        is_directory = serializers.BooleanField(source="is_dir")
        size = serializers.IntegerField(source="stat.st_size")

Output: Interface

.. code-block:: typescript

    export interface Path {
      name: string;
      suffix: string;
      suffixes: string[];
      stem: string;
      isDirectory: boolean;
      size: number;
    }

There are more examples in `test cases`_.

.. _test cases: https://github.com/jinkanhq/django-rest-tsg/tree/main/tests

Build Options
-----------------

All options are listed in the table below.

+--------------------+-------------+--------------------+
| Name               | Context     | Value              |
+====================+=============+====================+
| alias              | All         | ``str``            |
+--------------------+-------------+--------------------+
| build_dir (TODO)   | All         | ``str`` | ``Path`` |
+--------------------+-------------+--------------------+
| enforce_uppercase  | Enum        | ``bool`` (False)   |
+--------------------+-------------+--------------------+
