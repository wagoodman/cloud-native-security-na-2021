.PHONY: run
run:
	tkn pipeline start build-and-validate \
		-w name=share,volumeClaimTemplateFile=resources/pvc.yaml \
		--serviceaccount=build-bot

.PHONY: install-tekton
install-tekton:
	kubectl apply --filename https://storage.googleapis.com/tekton-releases-nightly/pipeline/latest/release.yaml
	kubectl apply --filename https://storage.googleapis.com/tekton-releases-nightly/dashboard/latest/tekton-dashboard-release.yaml


.PHONY: install
install: install-image-cache-pvc install-service-account install-fake-secret install-crds install-tasks install-pipelines

.PHONY: install-tasks
install-tasks: install-external-tasks install-local-tasks

.PHONY: install-fake-secret
install-fake-secret:
	# this isn't a real secret, we just need dummy data
	@kubectl create secret generic asset-token \
	--from-literal=username=devuser \
	--from-literal=token='12345A7a901b345678901234567890123456789012345678901234567890' || true

# .PHONY: enable-feature-flags
# enable-feature-flags:
# 	./scripts/enable-feature-flags.sh

.PHONY: install-image-cache-pvc
install-image-cache-pvc:
	./scripts/install-image-cache-pvc.sh

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