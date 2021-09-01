.PHONY: run
run:
	tkn pipeline start build-and-validate -w name=shared-data,volumeClaimTemplateFile=components/pvc.yaml

.PHONY: install
install: install-tasks install-pipelines

.PHONY: install-tasks
install-tasks:
	./scripts/install-tasks.sh
	
.PHONY: install-pipelines
install-pipelines:
	./scripts/install-pipelines.sh