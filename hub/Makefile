venv_dir=venv
python3=python3

check: $(venv_dir)/packages-installed
	$(venv_dir)/bin/python3 -m pytest -vvv -x --tb=native --no-print-logs --pythonwarnings=ignore $(pytest_args) tests

run: $(venv_dir)/packages-installed
	$(venv_dir)/bin/overwatch-hub --conf sample_conf.yaml

run_mongodb:
	mkdir -p mongo_data
	mongod --dbpath=mongo_data --bind_ip 127.0.0.1

$(venv_dir)/packages-installed: requirements.txt requirements-tests.txt
	test -d $(venv_dir) || $(python3) -m venv $(venv_dir)
	$(venv_dir)/bin/pip install -U pip wheel
	$(venv_dir)/bin/pip install -r requirements.txt
	$(venv_dir)/bin/pip install -r requirements-tests.txt
	$(venv_dir)/bin/pip install -e .
	touch $@

docker_build:
	docker build -t ow2-hub .
