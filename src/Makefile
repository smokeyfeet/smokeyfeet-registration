SRC=$(CURDIR)
TESTS_DIR=$(SRC)/tests

COVERAGE=coverage
MANAGE=$(SRC)/manage.py
PYTEST=pytest
RUFF=ruff

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
	$(RUFF) check $(SRC)
	$(RUFF) format --diff $(SRC)

lint-fix:
	$(RUFF) check --fix $(SRC)
	$(RUFF) format $(SRC)

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

upgrade-deps:
	pip-compile --upgrade --generate-hashes --resolver=backtracking ./requirements.in
	pip-compile --upgrade --generate-hashes --resolver=backtracking ./requirements-dev.in
	pip-sync requirements.txt requirements-dev.txt
