COVERAGE=coverage
PYTHON=python

clean:
	find $(CURDIR) -type d -name __pycache__ -exec rm -rf {} \;
	$(COVERAGE) erase

test:
	$(PYTHON) $(CURDIR)/manage.py test

coverage:
	$(COVERAGE) run $(CURDIR)/manage.py test
	$(COVERAGE) html
