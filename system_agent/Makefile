venv_dir=venv
python3=python3
conf=sample_configuration.yaml

check: $(venv_dir)/packages-installed
	$(venv_dir)/bin/python3 -m pytest -v --tb=native $(pytest_args) tests

run: $(venv_dir)/packages-installed
	$(venv_dir)/bin/overwatch-system-agent --conf $(conf)

$(venv_dir)/packages-installed: requirements.txt requirements-tests.txt
	test -d $(venv_dir) || $(python3) -m venv $(venv_dir)
	$(venv_dir)/bin/pip install -U pip wheel
	$(venv_dir)/bin/pip install -r requirements.txt
	$(venv_dir)/bin/pip install -r requirements-tests.txt
	$(venv_dir)/bin/pip install -e .
	touch $@
