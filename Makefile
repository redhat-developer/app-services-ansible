CONTAINER_ENGINE=$(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null)
IMAGE_NAME?=app-services-ansible_testing_image
CONTAINER_NAME?=app-services-ansible_testing_container

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"} /^[\/a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-35s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[34m\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Testing targets utilities to manage Docker images and containers
.PHONY: docker/test-image/build
docker/test-image/build: ## Build the test image
	$(CONTAINER_ENGINE) build -t $(IMAGE_NAME) .

.PHONY: docker/test-image/remove
docker/test-image/remove: ## Remove the test image
	$(CONTAINER_ENGINE) image rm $(IMAGE_NAME)

.PHONY: docker/test-container/bash
docker/test-container/bash: ## Execute interactive shell in the test container
	$(CONTAINER_ENGINE) run --name=$(CONTAINER_NAME) -ti $(IMAGE_NAME) /bin/bash

.PHONY: docker/test-container/stop-remove
docker/test-container/stop-remove: ## Stop and remove the test image
	$(CONTAINER_ENGINE) stop $(CONTAINER_NAME)
	$(CONTAINER_ENGINE) rm $(CONTAINER_NAME)

##@ Development utilities
.PHONY: setup 
setup: ## Run scripts/setup.sh script
	. ./scripts/setup.sh

.PHONY: local-dev
local-dev: ## Run scripts/local_dev.sh script
	. ./scripts/local_dev.sh
