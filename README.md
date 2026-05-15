# Enigma M3 Machine Simulator And Viewer

Implementation of the Enigma M3 cipher machine in C with interactive configuration and a Manim-based step by step visualization of the encryption signal path.

Example of video generated passing the letter T:

![gif](enigma.gif)

## Dependencies

- **C compiler**
- **python** w/ **Manim**

    ```bash
    python -m venv venv-manim       # create a virtual environment
    source venv-manim/bin/activate  # activate it
    pip install manim               # install the Manim library
    ```

    > **Note:** Manim also requires system-level dependencies (Cairo, Pango, LaTeX, FFmpeg).
    > See the [official Manim installation guide](https://docs.manim.community/en/stable/installation.html).

- **iosevka** font for the animation

## Usage

### CLI Encryption

Compile and run the standalone executable:

```bash
make run
```

The simulator will prompt you to configure the machine interactively:

1. Choose a plugboard configuration (up to 10 letter pairs)
2. Choose the reflector
3. Choose three rotors with relative starting positions (0–25) and ring settings (0–25)
4. Enter a word to encrypt/decrypt

> **Enigma is symmetric:** encrypting a ciphertext with the same settings produces the original plaintext.

### Manim Animation

The animation script (`main.py`) loads the shared library (`build/enigma.so`), prompts the user to configure the machine and visualizes the signal path of a single character through the machine.

#### Build the shared library

```bash
make shared
```

#### Run the animation

```bash
make animation
```

or invoke Manim directly with a specific quality preset:

```bash
manim -pql main.py Enigma   # 480p 15fps  (fast preview)
manim -pqm main.py Enigma   # 720p 30fps  (medium)
manim -pqh main.py Enigma   # 1080p 60fps (high quality)
```

The animation:

1. prompts you to configure the machine
2. asks you a letter to encrypt
3. renders a video of a step by step signal path animation

## Machine Configuration

The simulator supports the following historical components:

### Rotors

| Name | Wiring | Notch |
|------|--------|-------|
| Rotor I | EKMFLGDQVZNTOWYHXUSPAIBRCJ | Q |
| Rotor II | AJDKSIRUXBLHWTMCQGZNPYFVOE | E |
| Rotor III | BDFHJLCPRTXVZNYEIWGAKMUSQO | V |
| Rotor IV | ESOVPZJAYQUIRHXLNFTGKDCMWB | J |
| Rotor V | VZBRGITYUPSDNHLXAWMJQOFECK | Z |

### Reflectors

| Name | Wiring |
|------|--------|
| Reflector B | YRUHQSLDPXNGOKMIEBFZCWVJAT |
| Reflector C | FVPJIAOYEDRZXWGCTKUQSBNMHL |


## Testing

The implementation has been tested against two online Enigma simulators:

- <https://www.101computing.net/enigma-machine-emulator/>
- <https://www.cachesleuth.com/enigma.html>

## References

- [Cipher Machines and Cryptology](https://www.ciphermachinesandcryptology.com/en/enigmatech.htm) – Enigma technical details
- [Codes and Ciphers](https://www.codesandciphers.org.uk/enigma/rotorspec.htm) – Rotor specifications
- The Manim Community Developers. (2025). *Manim – Mathematical Animation Framework* [Computer software]. <https://www.manim.community/>

# License

MIT license
