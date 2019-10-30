test:
	@(python -m pytest django_multitenant/tests/ -k 'not concurrency')


dev-dependencies:
	pip install -r requirements/test.txt



release:
	python setup.py sdist
	twine upload --skip-existing dist/*
