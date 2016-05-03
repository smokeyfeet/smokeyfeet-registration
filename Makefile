PYTHON=python

clean:
	find $(CURDIR) -type d -name __pycache__ -exec rm -rf {} \;

test:
	$(PYTHON) manage.py test

