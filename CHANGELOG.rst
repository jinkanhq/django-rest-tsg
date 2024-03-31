0.1.10
-------------

* Bump python version to 3.12.
* Bump django version to 5.0.
* Bump djangorestframework version to 3.15.


0.1.9
-------------

* Bump djangorestframework-dataclasses version to 1.3.0.
* Fix nullable representation for field with allow_null as true.


0.1.8
-------------
* Bump django version to 4.2.

0.1.7
-------------
* Bump django version to 4.1.
* Bump djangorestframework version to 3.14.

0.1.6
-------------
* Fix missing dependencies when flatten DataclassSerializer.
* Write to file only if task content changes.

0.1.5
-------------

* Fix dependency path of import statements when build_dir is specified in options.

0.1.4
-------------

* Add task-level build_dir support.

0.1.3
-------------
* Enrich README content.
* Add builder logging.
* Fix alias failure.
* Fix aliases in typescript import statements.

0.1.2
-------------
* Get dataclass of DataclassSerializer from dataclass attribute when Meta is missing.
* Fix field type of trivial serializer.


0.1.1
-------------
* Fix annotated trivial type fallback.
* Skip ``typing`` types on dependency resolving.

0.1.0
-------------
Initial version.
