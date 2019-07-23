.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

export define ZIPAPP_BASHSCRIPT
	set -o errexit
    echo activating py3 ...
	source activate py3
    echo activating py2 ...
	source activate py2
	exit
	cd ansible_taskrunner
	for pyver in py2 py3;do
		echo Checking for embedded libraries in lib/$${pyver}
		if ! test -d lib/$${pyver};then
		  echo Creating lib/$${pyver}
		  mkdir lib/$${pyver}
		  echo Installing requirements to lib/$${pyver} ...
		  source activate $$pyver
		  pip install -t lib/$${pyver} -r ../requirements.txt
		fi
	done
	__version=$$(egrep '.*__version__ =' __init__.py | cut -d\  -f3 | tr -d "'")
	echo "Version is $${__version}"
	__release_dir=../release/$${__version}
	lint_result=$$(python cli.py --help)
	echo "Initial lint OK, proceeding with build"
	if [[ "$$OSTYPE" =~ .*msys.* ]];then 
	echo "OSType is Windows, nesting libdir ..."
	if test -d windows;then 
	  rm -rf windows
	else
	  mkdir windows
	fi
	cp -r lib plugins windows
	echo "Creating zip-app"
	make-zipapp -f cli.py -X __pycache__ -x .pyc -d windows
	if test -d windows;then rm -rf windows;fi
	else
	echo "OSType is most likely POSIX native"
	echo "Creating zip-app"
	make-zipapp -f cli.py -X __pycache__ -x .pyc
	fi
	mv cli tasks
	lint_result=$$(tasks --help)
	echo "Initial lint OK, proceeding with release"
	if ! test -d $${__release_dir};then mkdir -p $${__release_dir};fi
	mv -f tasks $${__release_dir}
	echo "Replacing current executable: $$(which tasks)"
	yes | cp $${__release_dir}/tasks $$(which tasks)
	if [[ -n $$deployment_host_and_path ]];then
	echo "Pushing up"
	scp_result=$$(scp $${__release_dir}/tasks $${deployment_host_and_path})
	fi	
endef

build-zipapp:; @ eval "$$ZIPAPP_BASHSCRIPT"

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 ansible_taskrunner tests

test: ## run tests quickly with the default Python
	python setup.py test

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source ansible_taskrunner setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/ansible_taskrunner.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ ansible_taskrunner
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install
