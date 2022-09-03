SRC=$(CURDIR)
TESTS_DIR=$(SRC)/tests

COVERAGE=coverage
MANAGE=$(SRC)/manage.py
PYTEST=pytest
BLACK=black
FLAKE8=flake8

DB_NAME=smokeyfeet

serve:
	$(MANAGE) runserver

clean:
	@echo "---> Cleaning project"
	find $(SRC) -name "*.pyc" -type f -delete
	find $(SRC) -type d -name __pycache__ -delete
	find $(SRC) -type f -name django-smokeyfeet.log -delete
	$(COVERAGE) erase
	rm -rf $(SRC)/htmlcov

test:
	@echo "---> Unit testing"
	$(PYTEST) -v $(TESTS_DIR)

test-coverage:
	@echo "---> Unit testing with coverage"
	$(COVERAGE) erase
	$(COVERAGE) run --source=$(SRC)/smokeyfeet -m $(PYTEST) -v $(TESTS_DIR)
	$(COVERAGE) html

lint:
	$(BLACK) --quiet --check --diff --exclude=/migrations/ $(SRC)/smokeyfeet $(TESTS_DIR)
	$(FLAKE8) --config $(SRC)/setup.cfg $(SRC)/smokeyfeet $(TESTS_DIR)

clobber:
	dropdb --if-exists $(DB_NAME)
	createdb $(DB_NAME)
	$(MANAGE) migrate
	$(MANAGE) makemigrations
	$(MANAGE) migrate
	$(MANAGE) loaddata $(SRC)/smokeyfeet/registration/fixtures/lunch_types.json
	$(MANAGE) loaddata $(SRC)/smokeyfeet/registration/fixtures/pass_types.json
	$(MANAGE) loaddata $(SRC)/smokeyfeet/minishop/fixtures/products.json
	DJANGO_SUPERUSER_PASSWORD=admin $(MANAGE) createsuperuser \
		--username admin --email noreply@example.tld --noinput

upgrade_deps:
	pip-compile --upgrade --generate-hashes ./requirements.in
	pip-compile --upgrade --generate-hashes ./requirements-dev.in
	pip-sync requirements.txt requirements-dev.txt
