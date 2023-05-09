CONTAINER_NAME := cafe_bar_info_system
IMAGE_NAME := cafe_bar_info_system

.PHONY: all build run stop clean

all: stop clean build run

build:
	@echo "Building Docker image..."
	@sudo docker build -t $(IMAGE_NAME) .

run: stop clean build
	@echo "Running Docker container..."
	@sudo docker run -d -p 5000:5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop:
	@echo "Stopping Docker container..."
	@sudo docker stop $(CONTAINER_NAME) || true

clean:
	@echo "Removing Docker container and image..."
	@sudo docker rm $(CONTAINER_NAME) || true
	@sudo docker rmi $(IMAGE_NAME) || true
