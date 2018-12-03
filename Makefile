run:
	docker run \
		--rm \
		-it \
		-p 9100:9100 \
    -v `pwd`/prints:/app/prints \
		honeynet-jetdirect

build:
	docker build \
		-t honeynet-jetdirect \
		.

clean:
	docker rmi honeynet-jetdirect

jetdirect:
	telnet localhost 9100
