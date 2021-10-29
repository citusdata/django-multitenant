test:
	DJANGO_SETTINGS_MODULE=django_multitenant.tests.settings py.test -s django_multitenant/tests/ -k 'not concurrency'


dev-dependencies:
	pip install -r requirements/test.txt

release-dependencies:
	pip install -r requirements/release.txt


release:
	python -m build --sdist
	twine check dist/*
	twine upload --skip-existing dist/*
