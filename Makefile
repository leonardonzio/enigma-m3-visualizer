CC=gcc
CFLAGS=-Wall -std=c99 -pedantic

all: build/enigma

build/enigma: enigma.c
	@mkdir -p build
	$(CC) $(CFLAGS) -o build/enigma enigma.c 

build/enigma.so: enigma.c
	@mkdir -p build
	$(CC) $(CFLAGS) -fPIC -shared -o build/enigma.so enigma.c

shared: build/enigma.so

run: build/enigma
	./build/enigma

animation: shared
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "u have to run: source venv_manim/bin/activate"; \
		exit 1; \
	fi
	@echo "using $$(which python)..."
	manim -p animation/main.py Enigma

clean:
	rm -f build/enigma*

.PHONY: all build/enigma build/enigma.so shared run animation clean
