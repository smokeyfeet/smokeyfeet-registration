COVERAGE=coverage
PYTHON=python

serve:
	$(PYTHON) $(CURDIR)/manage.py runserver

clean:
	@echo "---> Cleaning project"
	find $(CURDIR) -name "*.pyc" -type f -delete
	find $(CURDIR) -type d -name __pycache__ -delete
	find $(CURDIR) -type f -name django-smokeyfeet.log -delete
	$(COVERAGE) erase

test:
	@echo "---> Testing"
	$(PYTHON) $(CURDIR)/manage.py test

coverage:
	$(COVERAGE) run $(CURDIR)/manage.py test
	$(COVERAGE) html

lint:
	flake8 $(CURDIR)/smokeyfeet
