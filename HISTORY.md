=======
History
=======

## Release 2019-30-07 v0.0.19

* Cleaned up and improved available make-style functions 
  [013933c](https://github.com/berttejeda/ansible-taskrunner/commit/013933c3a6217225b4fe064c8e7ba96dba044f27)
* Account for additional edge-cases when parsing for make-style functions 
  [ba81cfa](https://github.com/berttejeda/ansible-taskrunner/commit/ba81cfab5c55bd2f4ea0e3047cf591e4c329040d)
* Don't attempt parsing the Taskfile for options help strings if the Taskfile is inaccessible [6a5c93d](https://github.com/berttejeda/ansible-taskrunner/commit/6a5c93da22d300c206021266a316d3e23f15a081)Don't attempt parsing the Taskfile for options help strings if the Taskfile is inaccessible
  [6a5c93d](https://github.com/berttejeda/ansible-taskrunner/commit/6a5c93da22d300c206021266a316d3e23f15a081)
* Fixed bug whereby the make-style function handler was not being added to list of functions available to subprocess
  [b7a2c8e](https://github.com/berttejeda/ansible-taskrunner/commit/b7a2c8eddea04bd285227459e737ded3d4fbdab1)
* Removed unused doc tasks
  [aeedcc5](https://github.com/berttejeda/ansible-taskrunner/commit/aeedcc5f06947e9c1f2152eced02933d47e79892)
* Added info for __tasks_file__ special variable
  [d93158f](https://github.com/berttejeda/ansible-taskrunner/commit/d93158f485afb85da42aeafaa6c3f7f93389274a)
* Updated examples, options documentation
  [ce26cda](https://github.com/berttejeda/ansible-taskrunner/commit/ce26cdad7492946f524ea0101d6c1890a8481130)
* Improved support for make-style functions
  [1ac4a6c](https://github.com/berttejeda/ansible-taskrunner/commit/1ac4a6c087adc22f49a75ccc850fe38810fd9f63)
  Refactored cli class name
  Added Makefile-style help message logic for cli-options
  Added support for make-style functions with python source
  Moved tasks from Makefile to Makefile.yaml
  Removed leftover 'bash' package from lib folder
* Initial commit of examples
  [52c3af4](https://github.com/berttejeda/ansible-taskrunner/commit/52c3af42e547efacaa55fee69e61f956d0a5dd44)

## Release 2019-30-07 v0.0.18

* First release on PyPI.

