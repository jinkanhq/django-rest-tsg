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

    from django_rest_tsg.build import build

    build_tasks = [
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
