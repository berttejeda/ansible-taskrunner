=======
History
=======

## Release 2019-09-27 v1.1.10

* Adjusted max content width for help messages [7052485](https://github.com/berttejeda/ansible-taskrunner/commit/70524851385d959b9509c45ecb94864ac1a480ba)

## Release 2019-09-27 v1.1.9

* Accounting for pypi package context for cli invocation logic [975d7a7](https://github.com/berttejeda/ansible-taskrunner/commit/975d7a74c27e534eb1994d2fa48af846c9763410)

## Release 2019-09-27 v1.1.8

* Added additional unit tests for the 'run' subcommand [cbb0607](https://github.com/berttejeda/ansible-taskrunner/commit/cbb06071719681c96fd50cfebc5e0dac781d9792)
* Moved pre-execution cli invocation logic to separate module [3e5d717](https://github.com/berttejeda/ansible-taskrunner/commit/3e5d717ef92b4d32496a5631f4cc6691cf4ebcf8)
* Fixed bug in Taskfile override logic [d825325](https://github.com/berttejeda/ansible-taskrunner/commit/d825325a1b69ee76b8d7d501f8448effdee6e9f3)

## Release 2019-09-27 v1.1.7

* Skip mutually exclusive cli options with broken associations [ebe1cb4](https://github.com/berttejeda/ansible-taskrunner/commit/ebe1cb4440c2d7c5915db42ca6a28f677f12733b)
* Main CLI interface now lends itself to unit/integration tests using click.testing [fbc6cf7](https://github.com/berttejeda/ansible-taskrunner/commit/fbc6cf717b4898d899eb128d9372643c292a7290)

## Release 2019-09-25 v1.1.6

* Fixed bug whereby built-in options weren't properly accounted for in the py2 cli reordering logic [be21143](https://github.com/berttejeda/ansible-taskrunner/commit/be21143552bb11c225452e16dd14aa950c5dbeb1)

## Release 2019-09-25 v1.1.5

* Implement simple string templating for cli options and help-related messages [751fa5e](https://github.com/berttejeda/ansible-taskrunner/commit/751fa5e8bc63c7f7bd8fe0ac97dfec13bdf7be94)

## Release 2019-09-23 v1.1.4

* Added error handling for variable interpolation [1cc2803](https://github.com/berttejeda/ansible-taskrunner/commit/1cc2803e22b83341a0d54503a89dfa8c3114c5f6)
* Added init actions for sftp settings file [8a7dc85](https://github.com/berttejeda/ansible-taskrunner/commit/8a7dc8534d05f99aa4894655fab0841cb826e9d5)

## Release 2019-09-23 v1.1.3

* Adjusted bastion mode options [f0e2bce](https://github.com/berttejeda/ansible-taskrunner/commit/f0e2bce3cc6adc103954ed01d12f724c059a0730)
* Fixed bug in cli re-ordering logic for Python 2.7.x [cb5e000](https://github.com/berttejeda/ansible-taskrunner/commit/cb5e0005a6ed34cae0700a2faad4e41016108422)
* Added a missing intermediary dictionary object [bd405ce](https://github.com/berttejeda/ansible-taskrunner/commit/bd405ce171c811856bf01416065c635432c78d96)
* Suppress warnings from paramiko unless debug mode is enabled [b623a8d](https://github.com/berttejeda/ansible-taskrunner/commit/b623a8dca705d71ab956961e6e8eaafb6c2184b6)
* Addressed bug in re-ordering of vars/cli options ordering for Pyton 2.x [dc82860](https://github.com/berttejeda/ansible-taskrunner/commit/dc828600fc361bd7cc0a6f8356d23957bb5ce9bc)
* Taskfile accidentally set to bash mode [4244faf](https://github.com/berttejeda/ansible-taskrunner/commit/4244faf6dd65213f6aa3f216621b94fc14fabe2f)

## Release 2019-09-20 v1.1.2

* Added support for mutually-exclusive cli options [0d8819b](https://github.com/berttejeda/ansible-taskrunner/commit/0d8819bbf68317c0098c1dd858f7c7e1ae9cfae4)
* Added support for multiple parameter sets [f607b0d](https://github.com/berttejeda/ansible-taskrunner/commit/f607b0d70aee9b8b8b335c8859f4596d083f397d)

## Release 2019-09-20 v1.1.1

* Addressed accidental inclusion of unecessary python module warning filters [ff6e898](https://github.com/berttejeda/ansible-taskrunner/commit/ff6e8981c8a79d85bccf076d781349c2374edef3)
* Refactored logging facility [a6dfba0](https://github.com/berttejeda/ansible-taskrunner/commit/a6dfba04ec8ae7442a1f02dac3e5c2cc1dde3394)

## Release 2019-09-20 v1.1.0

* Initial commit of bastion-mode codebase [7426a50](https://github.com/berttejeda/ansible-taskrunner/commit/7426a500defa4699d507038400293222f64e03f2)

## Release 2019-09-15 v1.0.2

* Utilize threading to better handle ctrl-c/breaking out of subprocess calls [c248c99](https://github.com/berttejeda/ansible-taskrunner/commit/c248c99e355e058f9e0d775c4ddd5fe45025a9f7)
* Renamed yamlc module to proc_mgmt [8e72a54](https://github.com/berttejeda/ansible-taskrunner/commit/8e72a54ff9db57109144ab9855ae6eb4361200dd)
* Fixed bug in logic for preserving variables/cli order for python 2.x [4c16bd3](https://github.com/berttejeda/ansible-taskrunner/commit/4c16bd3a8493b595bb28e915b02cf18b8d8740ba)
* Improved debugging for subprocess calls [e00dc4b](https://github.com/berttejeda/ansible-taskrunner/commit/e00dc4bd36e9b7baba860f592a8cd2ad46a2bb0e)
* Preserve order of variables and cli options for python 2.x [22d330c](https://github.com/berttejeda/ansible-taskrunner/commit/22d330ca8e91af3ff0a287d75e58582391376f23)
* Refactored handling of variables [ddbc787](https://github.com/berttejeda/ansible-taskrunner/commit/ddbc7870827c304f62a7ca8a733fd021745c7a27)
* Fixed formatting [ab21879](https://github.com/berttejeda/ansible-taskrunner/commit/ab21879959f1ee1895656c2fc0f1672b3c45f328)
* Added more documentation for variable declarations [2f4efa7](https://github.com/berttejeda/ansible-taskrunner/commit/2f4efa75f433b71e98f4e954456263697b5e1f45)

## Release 2019-05-08 v1.0.1

* Deleted unused library [255fcf1](https://github.com/berttejeda/ansible-taskrunner/commit/255fcf1999f901ef9d01318c40c916fcd8461f02)
* Added logic to automatically add triple-dashed options as bash vars in subprocess [2e06029](https://github.com/berttejeda/ansible-taskrunner/commit/2e060299b297dd1821ae4a9862b46658e0d211a2)

## Release 2019-30-07 v1.0.0

* Added support for make-style functions with ruby source [a07bd96](https://github.com/berttejeda/ansible-taskrunner/commit/a07bd96c84f0a1f41c79fe9e1c66d920d0bf1272)
* Fixed erroneous ansible task [56726be](https://github.com/berttejeda/ansible-taskrunner/commit/56726be9cdcd46f5842b370f28bcfa54cd241a81)
* The echo flag now includes logic for displaying the embedded inventory command [5f1cd13](https://github.com/berttejeda/ansible-taskrunner/commit/5f1cd13bf9eab583276196e913a43e27f0b88707)
* Corrected invalid names for make-style functions [da9a526](https://github.com/berttejeda/ansible-taskrunner/commit/da9a52602449c95a7abe5c37cd20bd2cc4f7ee8b)
* Fixed bug whereby raw args were not being properly read [5771e85](https://github.com/berttejeda/ansible-taskrunner/commit/5771e853189f854e207bfe036afa271869b31dcb)
  Decided to remove the '---r' built-in CLI option

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

