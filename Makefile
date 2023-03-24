export DJANGO_SETTINGS_MODULE=django_multitenant.tests.settings

test-dependencies:
	pip install -r requirements/test-requirements.txt 
	pip install Django=="${DJANGO_VERSION}"

test:
	 py.test  --cov-report xml --cov=django_multitenant/tests/. -s django_multitenant/tests/ -k 'not concurrency'

test-local:
	 py.test -s django_multitenant/tests/test_viewsets.py -k 'not concurrency'

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

