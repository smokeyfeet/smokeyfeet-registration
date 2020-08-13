SRC=$(CURDIR)

COVERAGE=coverage
DB_NAME=smokeyfeet
PYTHON=python
MANAGE=$(SRC)/manage.py

serve:
	$(MANAGE) runserver

clean:
	@echo "---> Cleaning project"
	find $(SRC) -name "*.pyc" -type f -delete
	find $(SRC) -type d -name __pycache__ -delete
	find $(SRC) -type f -name django-smokeyfeet.log -delete
	$(COVERAGE) erase

test:
	@echo "---> Testing"
	$(MANAGE) test

coverage:
	$(COVERAGE) run $(SRC)/manage.py test
	$(COVERAGE) html

lint:
	flake8 --config $(SRC)/setup.cfg $(SRC)/smokeyfeet $(SRC)/tests

clobber:
	dropdb --if-exists $(DB_NAME)
	createdb $(DB_NAME)
	$(MANAGE) migrate
	$(MANAGE) makemigrations
	$(MANAGE) migrate
	$(MANAGE) loaddata $(SRC)/smokeyfeet/registration/fixtures/lunch_types.json
	$(MANAGE) loaddata $(SRC)/smokeyfeet/registration/fixtures/pass_types.json
	DJANGO_SUPERUSER_PASSWORD=admin $(MANAGE) createsuperuser \
		--username admin --email noreply@example.tld # --noinput
