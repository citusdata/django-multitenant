export DJANGO_SETTINGS_MODULE=django_multitenant.tests.settings

test:
	py.test -s django_multitenant/tests/ -k 'not concurrency'

test-migrations:
	./manage.py migrate tests

revert-test-migrations:
	./manage.py migrate tests 0002_distribute
	# We fake the 0002_distribute rollback, because it uses lots of raw sql and
	# otherwise we have to add reverse_sql='' everywhere. The backwards
	# migration of 0001_initial will drop the tables anyway.
	./manage.py migrate --fake tests 0001_initial
	./manage.py migrate tests zero


dev-dependencies:
	pip install -r requirements/test.txt

release-dependencies:
	pip install -r requirements/release.txt


format:
	black .

format-check:
	black . --check

release:
	python -m build --sdist
	twine check dist/*
	twine upload --skip-existing dist/*
