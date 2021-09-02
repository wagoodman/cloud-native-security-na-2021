.PHONY: run
run:
	tkn pipeline start build-and-validate -w name=share,volumeClaimTemplateFile=components/pvc.yaml

.PHONY: install
install: install-tasks install-pipelines

.PHONY: install-tasks
install-tasks: install-external-tasks install-local-tasks

.PHONY: install-local-tasks
install-local-tasks:
	./scripts/install-local-tasks.sh

.PHONY: install-external-tasks
install-external-tasks:
	./scripts/install-external-tasks.sh
	

.PHONY: install-pipelines
install-pipelines:
	./scripts/install-pipelines.sh