.PHONY: run
run:
	tkn pipeline start build-and-validate \
		-w name=share,volumeClaimTemplateFile=resources/pvc.yaml \
		--serviceaccount=build-bot

.PHONY: install
install: install-service-account install-fake-secret install-crds install-tasks install-pipelines

.PHONY: install-tasks
install-tasks: install-external-tasks install-local-tasks

.PHONY: install-fake-secret
install-fake-secret:
	# this isn't a real secret, we just need dummy data
	@kubectl create secret generic asset-token \
	--from-literal=username=devuser \
	--from-literal=token='fake-token-value' || true

.PHONY: install-service-account
install-service-account:
	./scripts/install-service-account.sh

.PHONY: install-crds
install-crds:
	./scripts/install-crds.sh

.PHONY: install-external-tasks
install-external-tasks:
	./scripts/install-external-tasks.sh

.PHONY: install-local-tasks
install-local-tasks:
	./scripts/install-local-tasks.sh

.PHONY: install-pipelines
install-pipelines:
	./scripts/install-pipelines.sh