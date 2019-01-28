test:
	@(py.test -s django_multitenant/tests/ -k 'not concurrency')	


dev-dependencies:
	pip install -r requirements/test.txt
