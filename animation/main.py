from enum import Enum
from manim import *
import ctypes

def character_alphabet_index(char: str):
    return "ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(char)

def alphabet_character_at_index(index: int):
    return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[index]

# wiring constants
ROTOR_WIRINGS = {
    "Rotor I":   "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "Rotor II":  "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "Rotor III": "BDFHJLCPRTXVZNYEIWGAKMUSQO",
    "Rotor IV":  "ESOVPZJAYQUIRHXLNFTGKDCMWB",
    "Rotor V":   "VZBRGITYUPSDNHLXAWMJQOFECK",
}
REFLECTOR_WIRINGS = {
    "Reflector B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "Reflector C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}

# ctypes definitions
class EncryptionSteps(ctypes.Structure):
    """Mirrors EncryptionSteps in enigma.c"""
    _fields_ = [
        ('input_char',       ctypes.c_char),
        ('after_plugboard_1',ctypes.c_char),
        ('after_R_rotor',    ctypes.c_char),
        ('after_M_rotor',    ctypes.c_char),
        ('after_L_rotor',    ctypes.c_char),
        ('after_reflector',  ctypes.c_char),
        ('after_L_rotor_back',ctypes.c_char),
        ('after_M_rotor_back',ctypes.c_char),
        ('after_R_rotor_back',ctypes.c_char),
        ('after_plugboard_2',ctypes.c_char),
        ('output_char',      ctypes.c_char),
    ]

    def __str__(self) -> str:
        d = lambda b: b.decode('utf-8')
        return (
            f"Input char:        {d(self.input_char)}\n"
            f"After plugboard 1: {d(self.after_plugboard_1)}\n"
            f"After R rotor:     {d(self.after_R_rotor)}\n"
            f"After M rotor:     {d(self.after_M_rotor)}\n"
            f"After L rotor:     {d(self.after_L_rotor)}\n"
            f"After reflector:   {d(self.after_reflector)}\n"
            f"After L rotor back:{d(self.after_L_rotor_back)}\n"
            f"After M rotor back:{d(self.after_M_rotor_back)}\n"
            f"After R rotor back:{d(self.after_R_rotor_back)}\n"
            f"After plugboard 2: {d(self.after_plugboard_2)}\n"
            f"Output char:       {d(self.output_char)}"
        )


class _Rotor(ctypes.Structure):
    _fields_ = [
        ('wiring',       ctypes.c_char * 26),
        ('notch',        ctypes.c_char),
        ('position',     ctypes.c_int),
        ('ring_setting', ctypes.c_int),
        ('name',         ctypes.c_char_p),
    ]

class _Reflector(ctypes.Structure):
    _fields_ = [
        ('wiring', ctypes.c_char * 26),
        ('name',   ctypes.c_char_p),
    ]

class _Plugboard(ctypes.Structure):
    _fields_ = [
        ('wiring', ctypes.c_char * 26),
    ]

class _Enigma(ctypes.Structure):
    _fields_ = [
        ('rotors',    _Rotor * 3),
        ('reflector', _Reflector),
        ('plugboard', _Plugboard),
    ]


# scene
class Enigma(Scene):

    def create_rotor(
        self,
        wiring_str: str,
        outer_radius: float = 1.4,
        inner_radius: float = 1.2,
        font: str = "Iosevka",
        font_size: int = 20,
        letter_color: ManimColor = WHITE,
        orientation: str = "upright", # upright, radial, tangent
    ) -> VGroup:
        # base annulus (the rotor face as a ring)
        ring = Annulus(inner_radius=inner_radius, outer_radius=outer_radius)
        ring.set_fill(GRAY_E, opacity=1.0).set_stroke(GRAY_D, width=2)

        highlight = Annulus(
            inner_radius=(inner_radius + outer_radius) / 2 * 0.95,
            outer_radius=(inner_radius + outer_radius) / 2 * 1.05,
        )
        highlight.set_fill(GRAY_C, opacity=0.25).set_stroke(width=0)

        letters = VGroup()
        indices = VGroup()

        r_mid   = 0.5 * (inner_radius + outer_radius)
        r_index = outer_radius + 0.15 # distance of the 0..25 labels from the center
        n       = len(wiring_str) # usually 26

        for i, ch in enumerate(wiring_str):
            angle = (PI / 2) - i * (PI * 2 / n) # -i so clockwise

            pos_letter = np.array([np.cos(angle), np.sin(angle), 0.0]) * r_mid
            t = Text(ch, font=font, font_size=font_size, weight=BOLD)
            t.set_color(letter_color).set_stroke(BLACK, width=0.6, opacity=0.7)
            if orientation == "radial":
                t.rotate(angle)
            elif orientation == "tangent":
                t.rotate(angle - PI / 2)
            t.move_to(pos_letter)
            letters.add(t)

            pos_index = np.array([np.cos(angle), np.sin(angle), 0.0]) * r_index
            idx = Text(str(i), font=font, font_size=int(font_size * 0.6), weight=BOLD)
            idx.set_color(BLUE).set_stroke(BLACK, width=0.6, opacity=0.7)
            idx.move_to(pos_index)
            indices.add(idx)

        return VGroup(ring, highlight, letters, indices)

    def update_content(self, current_object, new_content, content_type="text"):
        """ update the content of a rotor/text object """
        if content_type == "text":
            new_object = Text(new_content, font_size=16, font="Iosevka")
            new_object.set_color_by_gradient(RED, BLUE, GREEN)
        elif content_type == "rotor":
            new_object = self.create_rotor(new_content) # new_content is a wiring string
        else:
            raise ValueError(f"content_type sconosciuto: {content_type}")
        
        new_object.move_to(current_object)
        self.play(Transform(current_object, new_object))
        return current_object

    def construct(self):
        # load shared library
        try:
            so_file = "build/enigma.so"
            lib = ctypes.CDLL(so_file)
        except OSError as e:
            print(f"Error loading shared library: {e}")
            return

        # setup_enigma(Enigma *e) -> prompts user, fills struct
        setup_enigma = lib.setup_enigma
        setup_enigma.restype  = None
        setup_enigma.argtypes = [ctypes.POINTER(_Enigma)]

        # trace_encrypt(char c, Enigma *e) -> EncryptionSteps
        trace_encrypt = lib.trace_encrypt
        trace_encrypt.restype  = EncryptionSteps
        trace_encrypt.argtypes = [ctypes.c_char, ctypes.POINTER(_Enigma)]

        # configure machine interactvly
        machine = _Enigma()
        setup_enigma(ctypes.byref(machine))

        # read back chosen names/wirings from the struct
        r_name  = [machine.rotors[i].name.decode('utf-8') for i in range(3)]
        r_wiring= [machine.rotors[i].wiring.decode('utf-8') for i in range(3)]
        ref_name= machine.reflector.name.decode('utf-8')
        ref_wir = machine.reflector.wiring.decode('utf-8')
        plug_wir= machine.plugboard.wiring.decode('utf-8')
        has_plugboard = (plug_wir != "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

        print("Type a letter to encrypt (A-Z): ", end="", flush=True)
        user_input = input().strip().upper()
        steps = trace_encrypt(user_input.encode('utf-8'), ctypes.byref(machine))
        print(steps)

        print("Animation? (y/n): ", end="", flush=True)
        if input().strip().lower() != 'y':
            print("Aborting animation..")
            return

        # intro slides
        testo = Text(
            "Benvenuto in questo esempio di animazione dell'attraversamento\n"
            "in avanti della macchina Enigma M3",
            font_size=24, font="Iosevka"
        )
        testo.set_color_by_gradient(RED, BLUE, GREEN)
        self.play(Write(testo))
        self.wait(3)

        self.update_content(
            testo,
            f"Questo visualizzatore utilizza come rotore di destra il {r_name[0]},\n"
            f"come rotore di mezzo il {r_name[1]}, e come rotore sinistro il {r_name[2]}."
        )
        self.wait(3)

        plug_desc = (
            "Il plugboard è configurato con scambi personalizzati"
            if has_plugboard else
            "Il plugboard non ha connessioni (nessuno scambio)"
        )
        self.update_content(
            testo,
            f"{plug_desc}.\nCome riflettore viene usato il {ref_name}."
        )
        self.wait(3)

        self.update_content(
            testo,
            "Quando l'utente preme una lettera, i rotori girano,\n"
            "e poi parte il segnale elettrico corrispondente a quella lettera"
        )
        self.wait(3)
        self.remove(testo)

        testo2 = Text("Qui un'immagine di esempio di un rotore:", font_size=16, font="Iosevka")
        testo2.set_color_by_gradient(RED, BLUE, GREEN).shift(UP*2)
        rotor_image = ImageMobject("imgs/cool_rotors.jpg")
        rotor_image.scale(1.8)
        self.play(Write(testo2))
        self.play(FadeIn(rotor_image), run_time=3)
        self.wait(3)
        self.play(FadeOut(rotor_image))
        self.play(FadeOut(testo2))

        # decode steps
        d = lambda b: b.decode('utf-8')
        input_char    = d(steps.input_char)
        after_R_rotor = d(steps.after_R_rotor)
        after_M_rotor = d(steps.after_M_rotor)
        after_L_rotor = d(steps.after_L_rotor)
        after_reflector = d(steps.after_reflector)
        output_char   = d(steps.output_char)

        # plugboard in
        after_plug1 = d(steps.after_plugboard_1)
        t1 = Text(
            f"Prima del rotore di destra, il segnale passa per il plugboard.\n"
            f"'{input_char}' → '{after_plug1}'"
            + ("  (nessuno scambio)" if input_char == after_plug1 else "  (scambiato!)"),
            font_size=16, font="Iosevka"
        )
        t1.set_color_by_gradient(RED, BLUE, GREEN).shift(UP)
        self.play(Write(t1))
        self.wait(3)

        # right rotor
        self.update_content(
            t1,
            f"Prendo il {r_name[0]} ({r_wiring[0]})\nnella sua posizione iniziale (indice 0)",
            "text"
        )
        self.wait(3)

        rotor_r = self.create_rotor(r_wiring[0])
        rotor_r.shift(DOWN)
        self.play(FadeIn(rotor_r))
        self.wait(3)

        self.update_content(
            t1,
            f"Ora premo il tasto '{input_char}'.\n"
            f"Il rotore di destra avanza sempre di una posizione\n"
            f"prima che il segnale elettrico parta",
            "text"
        )
        self.wait(3)

        input_char_t = Text(input_char, font_size=16, font="Iosevka")
        input_char_t.set_color_by_gradient(RED, ORANGE).shift(RIGHT*1.5)
        self.play(Write(input_char_t))

        idx_input = character_alphabet_index(after_plug1)
        idx_input_stepped = (idx_input + 1) % 26
        char_at_stepped = alphabet_character_at_index(idx_input_stepped)

        self.update_content(t1, "Questa rotazione sposta il corpo del rotore di 1/26 di giro", "text")
        self.wait(3)
        self.update_content(t1, "Il risultato è che i cablaggi interni non sono più allineati come prima:", "text")
        self.wait(3)
        self.update_content(
            t1,
            f"L'ingresso '{after_plug1}'\nnon si connette più al pin '{after_plug1}'({idx_input}),\n"
            f"ma a quello successivo modulo26, il pin '{char_at_stepped}'({idx_input_stepped})",
            "text"
        )
        self.wait(3)
        self.update_content(
            t1,
            f"Entra il segnale di '{after_plug1}' (idx{idx_input}),\n"
            f"ma a causa dello step il segnale segue il cablaggio al pin {idx_input_stepped} ({idx_input}+1 mod26)",
            "text"
        )
        self.wait(3)
        self.update_content(
            t1,
            f"Il cablaggio del {r_name[0]} al nuovo indice {idx_input_stepped} ha la lettera {r_wiring[0][idx_input_stepped]}",
            "text"
        )
        self.wait(3)

        letter = rotor_r[2][idx_input_stepped]
        self.play(letter.animate.set_color(YELLOW))
        self.wait(3)
        self.play(letter.animate.set_color(WHITE))
        self.wait(3)

        self.update_content(
            t1,
            f"Tuttavia anche l'uscita è sfalsata.\n"
            f"Il segnale esce dal contatto {r_wiring[0][idx_input_stepped]} (indice {character_alphabet_index(r_wiring[0][idx_input_stepped])}),\n"
            f"ma siccome il rotore è ruotato va sottratto l'offset: → '{after_R_rotor}'",
            "text"
        )
        self.wait(3)
        self.update_content(
            t1,
            f"Quindi '{input_char}' diventa '{after_R_rotor}' dopo il {r_name[0]}.\n"
            f"Il segnale '{after_R_rotor}' ora prosegue verso il rotore successivo.",
            "text"
        )
        self.wait(3)

        idx = r_wiring[0].index(after_R_rotor)
        letter_rotor = rotor_r[2][idx]
        self.play(letter_rotor.animate.set_color(YELLOW))
        self.wait(3)
        self.play(Transform(input_char_t, letter_rotor))
        self.wait(3)

        # middle rotor
        self.update_content(
            t1,
            f"La stessa cosa ora succede per i rotori successivi,\n"
            f"ma senza lo step in avanti (a meno che il rotore precedente\nnon si trovi sulla tacca).",
            "text"
        )
        self.wait(3)
        self.update_content(t1, f"Ora prendo il rotore di mezzo ({r_name[1]}):", "text")

        # removing old rotor and creating the new one
        self.remove(rotor_r, input_char_t)
        after_R_rotor_t = Text(after_R_rotor, font_size=16, font="Iosevka")
        after_R_rotor_t.set_color_by_gradient(RED, ORANGE).shift(RIGHT*1.5)
        self.play(FadeIn(after_R_rotor_t))

        rotor_m = self.create_rotor(r_wiring[1])
        rotor_m.shift(DOWN)
        self.play(FadeIn(rotor_m))
        self.wait(3)

        self.update_content(
            t1,
            f"La lettera '{after_R_rotor}' (indice {character_alphabet_index(after_R_rotor)}) entra nel rotore,\n"
            f"e corrisponde alla lettera '{after_M_rotor}' sul {r_name[1]}.",
            "text"
        )
        self.wait(3)

        idx = character_alphabet_index(after_R_rotor)
        self.play(
            rotor_m[2][idx].animate.set_color(YELLOW),
            rotor_m[3][idx].animate.set_color(YELLOW),
        )
        self.wait(3)
        self.play(Transform(after_R_rotor_t, rotor_m[2][idx]))
        self.wait(3)

        # left rotor
        self.update_content(t1, f"Infine prendo il rotore sinistro ({r_name[2]}):", "text")

        self.remove(rotor_m, after_R_rotor_t)
        after_M_rotor_t = Text(after_M_rotor, font_size=16, font="Iosevka")
        after_M_rotor_t.set_color_by_gradient(RED, ORANGE).shift(RIGHT*1.5)
        self.play(FadeIn(after_M_rotor_t))

        rotor_l = self.create_rotor(r_wiring[2])
        rotor_l.shift(DOWN)
        self.play(FadeIn(rotor_l))
        self.wait(3)

        self.update_content(
            t1,
            f"La lettera '{after_M_rotor}' (indice {character_alphabet_index(after_M_rotor)}) entra nel rotore,\n"
            f"e corrisponde alla lettera '{after_L_rotor}' sul {r_name[2]}.",
            "text"
        )
        self.wait(3)

        idx = character_alphabet_index(after_M_rotor)
        self.play(
            rotor_l[2][idx].animate.set_color(YELLOW),
            rotor_l[3][idx].animate.set_color(YELLOW),
        )
        self.wait(3)
        self.play(Transform(after_M_rotor_t, rotor_l[2][idx]))
        self.wait(3)

        # reflector
        self.update_content(
            t1,
            f"Ora i tre rotori sono stati attraversati.\n"
            f"Il segnale giunge al riflettore ({ref_name}):",
            "text"
        )

        self.remove(rotor_l, after_M_rotor_t)
        after_L_rotor_t = Text(after_L_rotor, font_size=16, font="Iosevka")
        after_L_rotor_t.set_color_by_gradient(RED, ORANGE).shift(RIGHT*1.5)
        self.play(FadeIn(after_L_rotor_t))

        reflector_mob = self.create_rotor(ref_wir)
        reflector_mob.shift(DOWN)
        self.play(FadeIn(reflector_mob))
        self.wait(3)

        self.update_content(
            t1,
            f"Il riflettore inverte il percorso del segnale.\n"
            f"'{after_L_rotor}' (indice {character_alphabet_index(after_L_rotor)}) è cablato a '{after_reflector}'.\n"
            f"Il segnale torna indietro nei rotori partendo da '{after_reflector}'.",
            "text"
        )
        self.wait(3)

        idx = character_alphabet_index(after_L_rotor)
        self.play(
            reflector_mob[2][idx].animate.set_color(YELLOW),
            reflector_mob[3][idx].animate.set_color(YELLOW),
        )
        self.wait(3)
        self.play(Transform(after_L_rotor_t, reflector_mob[2][idx]))
        self.wait(3)

        # return path..
        self.remove(reflector_mob, after_L_rotor_t)

        after_plug2 = d(steps.after_plugboard_2)
        self.update_content(
            t1,
            f"Una volta uscito dal riflettore, il segnale attraversa di nuovo i tre rotori in senso inverso\n"
            f"({r_name[2]} → {r_name[1]} → {r_name[0]}), seguendo gli stessi cablaggi ma al contrario.",
            "text"
        )
        self.wait(3)

        self.update_content(
            t1,
            f"Dopo l'ultimo passaggio nel plugboard ('{d(steps.after_R_rotor_back)}' → '{after_plug2}'),\n"
            f"il segnale arriva al pannello delle lampadine.\n"
            f"La lettera cifrata finale è '{output_char}'.",
            "text"
        )
        self.wait(3)
