=======
History
=======

## Release 2020-01-13 v1.4.0

* Feature/win32 colorize (#117) [4717d68](https://github.com/berttejeda/ansible-taskrunner/commit/4717d68db3fe28849ba2e62c9100e1c4fa9dd692)

## Release 2020-01-13 v1.3.9

* Address bug whereby raw args were being interpreted as an array instead of a string [54e3245](https://github.com/berttejeda/ansible-taskrunner/commit/54e3245945085cde64c518b1734f0815fb605d13)
* When unspecified, raw args should evaluate to empty string, not None [4f2ef3f](https://github.com/berttejeda/ansible-taskrunner/commit/4f2ef3fdae25373a9a3fb1eebdb7695420f9ad84)

## Release 2020-01-13 v1.3.8

* Add ability to completely suppress output [17a9f32](https://github.com/berttejeda/ansible-taskrunner/commit/17a9f328b23b3025436060f6e967d3079aea680b)
* Anything after '---raw' is passed down directly to the subprocess (#111) [236c270](https://github.com/berttejeda/ansible-taskrunner/commit/236c27005a558594fe3bf5206ff1c673a5adaa16)

## Release 2019-12-24 v1.3.7

* Ensure the main process return code matches that of the subprocess [44a2540](https://github.com/berttejeda/ansible-taskrunner/commit/44a25409d862a5322a0820e99533727eefa148fc)

## Release 2019-11-11 v1.3.6

* Refactor git diff command and embedded inventory file logic [330d5de](https://github.com/berttejeda/ansible-taskrunner/commit/330d5de010758e6467312afa827863ba2388e073)
* Skip deleted files when syncing local git folder to remote [64943b1](https://github.com/berttejeda/ansible-taskrunner/commit/64943b1c9c62fc8192d6d35e17db5002dfb995a9)

## Release 2019-11-04 v1.3.5

* Catch potential crash due to unexpected parameter mapping (python 2.x) [3f37e3e](https://github.com/berttejeda/ansible-taskrunner/commit/3f37e3e6c3bfa6cafc66fa5db5514f81e91879a2)

## Release 2019-11-04 v1.3.4

* Import missing logging module [56b3ca4](https://github.com/berttejeda/ansible-taskrunner/commit/56b3ca4292a189d169937efc5d8c3a7dbcfb0563)
* Add missing logger instantiation [02a6656](https://github.com/berttejeda/ansible-taskrunner/commit/02a6656345999c9d8568f499196856aba0f5b566)

## Release 2019-11-04 v1.3.3

* Fixed bug in cli invocation when specifying taskfile override [7a07d1a](https://github.com/berttejeda/ansible-taskrunner/commit/7a07d1af4060d96a487df4a8a69e347a94deb56e)
* Removed dependency on crayons package for ansi colors [9d985ef](https://github.com/berttejeda/ansible-taskrunner/commit/9d985ef7f4791e81aecad6475242d18050f6a8f9)
* Support for ad-hoc bastion-mode (no sftp config file) [9d985ef](https://github.com/berttejeda/ansible-taskrunner/commit/9d985ef7f4791e81aecad6475242d18050f6a8f9)

## Release 2019-11-03 v1.3.2

* Values from env should only be enabled by option tag [a792c52](https://github.com/berttejeda/ansible-taskrunner/commit/a792c5200da38ec59106f84a031e8298e7a6fb0b)

## Release 2019-11-03 v1.3.1

* Add support for choice options [5778948](https://github.com/berttejeda/ansible-taskrunner/commit/577894802bb3ce29cdd2bb298939eeeae6323371)
* Support for option values from environment variables [34f8c7b](https://github.com/berttejeda/ansible-taskrunner/commit/34f8c7b499c987c35ae2c1ad9ca5c9c20ab8c893)
* Added functionality for defining secure/insecure prompt options [1f43b63](https://github.com/berttejeda/ansible-taskrunner/commit/1f43b63f4fc3e5c93011ad93af374d3da46850d1)

## Release 2019-10-15 v1.3.0

* Bastion mode no longer depends on remote tasks command [e421130](https://github.com/berttejeda/ansible-taskrunner/commit/e4211305e931373327d3ccbc54367c90c60eefd9)

## Release 2019-10-15 v1.2.11

* Simplified options for main cli function [4abb784](https://github.com/berttejeda/ansible-taskrunner/commit/4abb7844b6c35379b1201e2ac4a6dcfee2d84615)
* Account for paramsets when deriving remote command [ac896c1](https://github.com/berttejeda/ansible-taskrunner/commit/ac896c19bcb4e74cbd89906e1c63cd680d39529b)
* Honors stderr/returncode for ansible cli provider [5601c61](https://github.com/berttejeda/ansible-taskrunner/commit/5601c618523085cf8b04d4a1a566c9ab1e325672)
* Reduce logging verbosity for paramiko client [126aad9](https://github.com/berttejeda/ansible-taskrunner/commit/126aad9aad8b30c77cbf6e73a9a2ce3ae039a266)

## Release 2019-10-11 v1.2.10

* Fixed invalid inventory in sample Taskfile.yaml [798b0b7](https://github.com/berttejeda/ansible-taskrunner/commit/798b0b789af627ca5f233e0111b37666b2c1e959)

## Release 2019-10-11 v1.2.9

* Incorrect credentials variables for pypi make-mode function [86d8323](https://github.com/berttejeda/ansible-taskrunner/commit/86d8323e40a8eed54984cdedc959289c6cf3e554)
* Fixed bug whereby kwargs was being rebuilt incorrectly [7c511ff](https://github.com/berttejeda/ansible-taskrunner/commit/7c511ffa3630342554cab06bf16fbe220eedf8bf)
* Added variable for zip-app release dir [8e0d73e](https://github.com/berttejeda/ansible-taskrunner/commit/8e0d73e9cf45aaf216055302ce31951a594328b3)

## Release 2019-10-11 v1.2.8

* Fixed minor syntax error in Taskfile init sample [bc8748f](https://github.com/berttejeda/ansible-taskrunner/commit/bc8748fcafaa015f0904e0b0c6334fa03efba672)
* Allow override of ssh/sftp port for init subcommand [578ac2a](https://github.com/berttejeda/ansible-taskrunner/commit/578ac2aa22236150bbd9eae90a58e6e53bc7865b)
* Default vars should be included in ansible extra options [312f8ef](https://github.com/berttejeda/ansible-taskrunner/commit/312f8ef2ed495a50e709b9b1f4ba4f40e2d919b1)
* Syspath was not being set properly for zipapp [9ee7df7](https://github.com/berttejeda/ansible-taskrunner/commit/9ee7df78738469dc65b91b7b14969c3c4800cefc)

## Release 2019-10-10 v1.2.7

* Fixed crash bug triggered by missing inventory key [c7cb0d2](https://github.com/berttejeda/ansible-taskrunner/commit/c7cb0d23b1a8a9344362edae333e8d14fe942aae)
* SFTP Sync now creates intermediate directories [320d93b](https://github.com/berttejeda/ansible-taskrunner/commit/320d93b032c45cc67b782c414a64e0ff9cf7b71f)
* Changed README.html template [e91dc3c](https://github.com/berttejeda/ansible-taskrunner/commit/e91dc3c514f698bbdc302cf8ee063ddafc737022)
* Added tutorial and adjusted environment [b484fc7](https://github.com/berttejeda/ansible-taskrunner/commit/b484fc72962af3ef24388ab1d3557e7876963f42)
* Minor fix in msi-builder function for Makefile.yaml [5c800fa](https://github.com/berttejeda/ansible-taskrunner/commit/5c800fa7d0b80ddd2c005e2441e1bed00666e880)

## Release 2019-10-03 v1.2.6

* Added support files for msi release [d719aa8](https://github.com/berttejeda/ansible-taskrunner/commit/d719aa8853bfa977a8e528295348628e452ba9c5)
* Allow bastion_mode settings to be overriden by config file [7496274](https://github.com/berttejeda/ansible-taskrunner/commit/749627495279f3697555bc1b661ac30f22b4e10a)
* Initial commit of cx_freeze setup logic [2f0af83](https://github.com/berttejeda/ansible-taskrunner/commit/2f0af83b5cbab0341676b52f90b22c611a94c57c)

## Release 2019-10-03 v1.2.5

* Fixed bug whereby modification time was being ignored (bastion mode) [6af8611](https://github.com/berttejeda/ansible-taskrunner/commit/6af86116f73922a982fdc578cca5e50c1c097f77)

## Release 2019-10-03 v1.2.4

* Fixed bug in sync logic whereby sync action was causing local dir to be nested in remote [6fe86b9](https://github.com/berttejeda/ansible-taskrunner/commit/6fe86b988b7f34eac091296aa528b4d34e11336f)
* Refactored sftp sync logic for non-git local dirs (bastion mode) [6bc786e](https://github.com/berttejeda/ansible-taskrunner/commit/6bc786e50734a7f6bbbca5eb8931974be752b833)

## Release 2019-10-03 v1.2.3

* Fixed minor bug in import path for sshutil library [278f0d5](https://github.com/berttejeda/ansible-taskrunner/commit/278f0d5dd8c17e2ae56bb25a2635855197058e84)

## Release 2019-10-03 v1.2.2

* Addressed bug whereby if no config is found, certain globals don't get initialized [fa1f7f1](https://github.com/berttejeda/ansible-taskrunner/commit/fa1f7f1993737a47265bbcb3d38ceb04e6491d7f)

## Release 2019-10-03 v1.2.1

* Removed bogus print statement leftover from recent troubleshooting [88be8a9](https://github.com/berttejeda/ansible-taskrunner/commit/88be8a9350ad33504d8ee74e8f403982c0400921)
* Moved some hard-coded values to the app config [e853ce0](https://github.com/berttejeda/ansible-taskrunner/commit/e853ce07ff1e1887e64a8fff2d29a03e4cb6ef37)
* Refactored misc vars [2c7c6eb](https://github.com/berttejeda/ansible-taskrunner/commit/2c7c6eb4ffc41fdf1e751eb7f4d02b3c46beed9e)
* Added colorized output for help examples [645621c](https://github.com/berttejeda/ansible-taskrunner/commit/645621cbb4f5338e03e81302231bf540213a9d4c)

## Release 2019-10-03 v1.2.0

* Renamed library path and refactored imports [afebb06](https://github.com/berttejeda/ansible-taskrunner/commit/afebb06433254acc9e6004978615eebd92c7c18d)

## Release 2019-10-03 v1.1.11

* We can now package the script as a Windows MSI via cx_freeze [18397c1](https://github.com/berttejeda/ansible-taskrunner/commit/18397c1e202b5a4884d047bbe2c37b2b2b253675)
* Fixed syntax error [4b43f44](https://github.com/berttejeda/ansible-taskrunner/commit/4b43f445722fd9da51b716a3f01cb8232479d69f)
* No more tampering [with] sys.path (unless zipapp) [07fb148](https://github.com/berttejeda/ansible-taskrunner/commit/07fb14810b3cdae18c8554b50504709a5d0a3fbf)
* Added Bastion Mode instructions [72f2a13](https://github.com/berttejeda/ansible-taskrunner/commit/72f2a13bdba1fd89e1cd7166fbbf5bddaea9fa10)
* Added cli option for overriding ssh key file [86a0d45](https://github.com/berttejeda/ansible-taskrunner/commit/86a0d4559e796ef82fa5f384741931771dd96c4f)
* Adjusted bastion mode sync logic to quit if we fail to create remote dir [0084ce5](https://github.com/berttejeda/ansible-taskrunner/commit/0084ce53086ad0b6c502bbb48914982d893b8913)
* Added bastion-mode config initialization logic to the init subcommand [39b332e](https://github.com/berttejeda/ansible-taskrunner/commit/39b332e013918c9474a8dc9d75dca61ee33e4464)
* Fixed inconsistencies in bastion mode remote command strings [8ddef53](https://github.com/berttejeda/ansible-taskrunner/commit/8ddef5356b245aa19c5bb8dd45fb27c4c36d780b)
* Fixed bug whereby script was being stripped from determinant of commandline invocation [2f445bf](https://github.com/berttejeda/ansible-taskrunner/commit/2f445bf9bfc5aa1d09b420fe35373dafd1a76b39)
* Added section on unit tests [7b3fa34](https://github.com/berttejeda/ansible-taskrunner/commit/7b3fa34dc3895fe569c2670895b313d685dcf5ee)

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

