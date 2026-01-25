ROOT := $(shell pwd)/src
PY := python3

.PHONY: help install server consumer-run consumer-alert consumer-fetch device-sim external-sim lint

help:
	@echo "Makefile targets:"
	@echo "  make install           # install python deps from requirements.txt"
	@echo "  make server            # run API server (uvicorn src.main:app)"
	@echo "  make consumer-run CONSUMER_TYPE=<type>  # run consumer by type"
	@echo "  make consumer-alert    # run alert_evaluator consumer"
	@echo "  make consumer-fetch    # run fetch_external_source consumer"
	@echo "  make device-sim        # run device simulator script"
	@echo "  make external-sim      # run external source simulator"

install:
	$(PY) -m pip install -r requirements.txt

server:
	@echo "Starting API server on port 8001"
	PYTHONPATH=$(ROOT) MODE=server $(PY) -m uvicorn src.main:app --reload --port 8001

consumer-run:
	@if [ -z "$(CONSUMER_TYPE)" ]; then \
		echo "Error: CONSUMER_TYPE not set. Example: make consumer-run CONSUMER_TYPE=fetch_external_source"; exit 1; \
	fi
	@echo "Starting consumer: $(CONSUMER_TYPE)"
	PYTHONPATH=$(ROOT) MODE=consumer CONSUMER_TYPE=$(CONSUMER_TYPE) $(PY) -m src.main

consumer-alert:
	@echo "Starting alert_evaluator consumer"
	PYTHONPATH=$(ROOT) MODE=consumer CONSUMER_TYPE=alert_evaluator $(PY) -m src.main

consumer-fetch:
	@echo "Starting fetch_external_source consumer"
	PYTHONPATH=$(ROOT) MODE=consumer CONSUMER_TYPE=fetch_external_source $(PY) -m src.main

device-sim:
	@echo "Running device simulator"
	PYTHONPATH=$(ROOT) $(PY) src/scripts/device_simulator.py

external-sim:
	@echo "Running external source simulator"
	PYTHONPATH=$(ROOT) $(PY) src/scripts/external_source.py

lint:
	@echo "No lint target configured; add commands here (e.g. flake8, ruff)"
