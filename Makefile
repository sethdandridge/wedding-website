PYTHON_VERSION ?= 3.10.6


install: SHELL_INIT_FILES ?= $(wildcard ~/.bash_profile ~/.zshrc)
install:
	python -m venv .env
	( \
		. .env/bin/activate; \
		pip install -r requirements.txt; \
		pre-commit install; \
    )
