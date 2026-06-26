IMAGE   := homelab/jupyter
CONTAINER := homelab-jupyter
VOLUME  := homelab-jupyter-data
PORT    := 8888

.PHONY: build run stop shell logs clean clean-all

build:
	docker build -t $(IMAGE) .

run: build
	docker run -d \
		--name $(CONTAINER) \
		-p $(PORT):8888 \
		-v $(VOLUME):/var/jupyter-data \
		-e JUPYTER_TOKEN="change-your-token" \
		$(IMAGE)
	@echo "JupyterLab → http://localhost:$(PORT)"

stop:
	docker rm -f $(CONTAINER) 2>/dev/null || true

shell: build
	docker run -it --rm \
		--name $(CONTAINER)-shell \
		-v $(VOLUME):/var/jupyter-data \
		$(IMAGE) bash

logs:
	docker logs -f $(CONTAINER)

# Remove container only; volume (user packages + notebooks) is kept
clean: stop

# Remove container AND volume — wipes all user data
clean-all: stop
	docker volume rm $(VOLUME) 2>/dev/null || true
