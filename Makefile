CODE = coreutils tests

.PHONY: pretty lint tests

pretty:
	python3 -m black --target-version py36 --skip-string-normalization $(CODE)
	python3 -m isort --apply --recursive $(CODE)
	python3 -m unify --in-place --recursive $(CODE)

lint:
	python3 -m black --target-version py36 --check --skip-string-normalization $(CODE)
	python3 -m flake8 --jobs 4 --statistics $(CODE)
	python3 -m pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	python3 -m mypy $(CODE)

tests:
	python -m pytest tests -vvv

lock:
	@rm -f poetry.lock
	python3 -m poetry lock

help:
	cat Makefile
