export DOCKER_BUILDKIT=1

all: build-all scan

build-all: build

build:
	docker-compose build costs-to-metrics

scan:
	trivy --exit-code 0 --severity MEDIUM,HIGH costs-to-metrics:latest
	trivy --exit-code 1 --severity CRITICAL costs-to-metrics:latest
