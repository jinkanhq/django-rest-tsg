.. image:: https://github.com/jinkanhq/django-rest-tsg/actions/workflows/coverage.yml/badge.svg
    :target: https://github.com/jinkanhq/django-rest-tsg/actions/workflows/coverage.yml

.. image:: https://codecov.io/gh/jinkanhq/django-rest-tsg/branch/main/graph/badge.svg?token=LX8E3QB541
    :target: https://codecov.io/gh/jinkanhq/django-rest-tsg

.. image:: https://badge.fury.io/py/django-rest-tsg.svg
    :target: https://badge.fury.io/py/django-rest-tsg

django-rest-tsg
====================

A typescript code generator for Django Rest Framework.

Usage
--------

Install using ``pip``

.. code-block:: bash

  $ pip install django_rest_tsg

Put a ``tsgconfig.py`` file with build tasks into your django project's root.

.. code-block:: python

    from django.conf import settings
    from django_rest_tsg.build import build

    BUILD_DIR = settings.BASE_DIR / 'app/src/core'

    BUILD_TASKS = [
        build(Foo),
        build(BarSerializer, 'app/src/app/core', {'alias': 'Foobar'}),
    ]

Add ``django_rest_tsg`` to your ``INSTALLED_APPS``.

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'django_rest_tsg'
    ]

Run ``buildtypescript`` command on ``manage.py``.

.. code-block:: bash

    $ python manage.py buildtypescript

Or you can switch to another place.

.. code-block:: bash

    $ python manage.py buildtypescript --build-dir /somewhere/you/
