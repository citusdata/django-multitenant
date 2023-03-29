export DJANGO_SETTINGS_MODULE=django_multitenant.tests.settings

test-dependencies:
	pip install -r requirements/test-requirements.txt 
	pip install Django=="${DJANGO_VERSION}"
	pip install djangorestframework

test:
	py.test  --cov-report xml --cov=django_multitenant/tests/. -s django_multitenant/tests/ -k 'not concurrency' --ignore django_multitenant/tests/test_missing_modules.py

test-missing-modules:
	# Test that the package works without the djangorestframework
	pip uninstall -y djangorestframework

	# We need to remove the rest_framework from the settings.py.
	# Normally, application without rest_framework will not be installed in setting file.
	# In our application we are installing rest_framework in test settings file to test the rest_framework related tasks. 
	cp django_multitenant/tests/settings.py django_multitenant/tests/settings.py.bak
	sed -i '/INSTALLED_APPS/{n; /rest_framework/d;}' django_multitenant/tests/settings.py
	py.test -s --cov-report xml --cov=django_multitenant/tests/. django_multitenant/tests/test_missing_modules.py -k 'not concurrency'
	# Revert the changes in settings.py
	mv django_multitenant/tests/settings.py.bak django_multitenant/tests/settings.py

test-migrations:
	./manage.py migrate tests

revert-test-migrations:
	./manage.py migrate tests 0002_distribute
	# We fake the 0002_distribute rollback, because it uses lots of raw sql and
	# otherwise we have to add reverse_sql='' everywhere. The backwards
	# migration of 0001_initial will drop the tables anyway.
	./manage.py migrate --fake tests 0001_initial
	./manage.py migrate tests zero

release-dependencies:
	pip install -r requirements/release-requirements.txt

format:
	black .

format-check:
	black --version
	black . --check

lint:
	prospector -X  --profile-path .prospector.yaml

release:
	python -m build --sdist
	twine check dist/*
	twine upload --skip-existing dist/*

test-model:
	 py.test  -s django_multitenant/tests/test_models.py -k 'not concurrency'

