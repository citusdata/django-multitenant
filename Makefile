test:
	DJANGO_SETTINGS_MODULE=django_multitenant.tests.settings py.test -s django_multitenant/tests/ -k 'not concurrency'


dev-dependencies:
	pip install -r requirements/test.txt



release:
	python setup.py sdist
	twine upload --skip-existing dist/*
