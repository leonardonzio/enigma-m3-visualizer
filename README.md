# Enigma M3 Machine Simulator And Viewer

Implementation of the Enigma M3 cipher machine with interactive configuration, and Manim visualization.

Example of video generated passing the letter H:

![gif](enigma.gif)

## Dependencies

- Python
- Manim

```bash
python -m venv venv-manim       # setup a virtual environment
source venv-manim/bin/activate  # source it
pip install manim               # install the manim library needed for the animation
```

## Usage

### CLI Encryption

Run the compiled executable:

```bash
make run
```

The simulator will prompt you to:
1. choose a plugboard configuration
2. choose a reflector
3. choose the three rotors
4. what word to encrypt/decrypt

### Manim Animation

The animation script (`main.py`) loads the shared library and visualizes the encryption of a single character through the rotor system.

#### Setup

Ensure the shared library is built:

```bash
make shared
```

#### Running the animation

```bash
make animation
```

or with specific rendering options:

```bash
manim -pql main.py Enigma # Render at 480p15fps
manim -pqh main.py Enigma # Render at 720p30fps
manim -pqh main.py Enigma # Render at 1080p60fps
```

The animation:

1. prompts for a single letter to demonstrate the encrypting process
2. visualize step-by-step the signal path through rotors
3. renders the video to media/videos/...

The animation uses the ctypes library to interface itself with the C simulator

## Testing

The implementation has been tested against two online Enigma simulator:

- https://www.101computing.net/enigma-machine-emulator/
- https://www.cachesleuth.com/enigma.html

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make all` or `make` | Compile standalone executable to _build/enigma_ |
| `make run` | Build and run the standalone CLI |
| `make shared` | Compile shared library to _build/enigma.so_ |
| `make animation` | Run the animation |
| `make clean` | Remove compiled binaries |


## References

- [Cipher Machines and Cryptology](https://www.ciphermachinesandcryptology.com/en/enigmatech.htm) – Enigma technical details
- [Codes and Ciphers](https://www.codesandciphers.org.uk/enigma/rotorspec.htm) – Rotor specifications
- The Manim Community Developers. (2025). Manim – Mathematical Animation Framework (Version v0.19.0) [Computer software]. https://www.manim.community/
