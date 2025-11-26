from enum import Enum
from manim import *
import ctypes

def character_alphabet_index(char: str):
    return Wiring.ALPHABET.value.index(char)

def alphabet_character_at_index(index: int):
    return Wiring.ALPHABET.value[index]

class Wiring(Enum):
    """
    enum to match the rotor/reflector wirings in enigma library
    """
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ROTOR_I = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
    ROTOR_II = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
    ROTOR_III = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
    REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"


class EncryptionSteps(ctypes.Structure):
    """
    struct to match EncryptionSteps in enigma.c
    """
    _fields_ = [
        ('input_char', ctypes.c_char),
        ('after_plugboard_1', ctypes.c_char),
        ('after_R_rotor', ctypes.c_char),
        ('after_M_rotor', ctypes.c_char),
        ('after_L_rotor', ctypes.c_char),
        ('after_reflector', ctypes.c_char),
        ('after_L_rotor_back', ctypes.c_char),
        ('after_M_rotor_back', ctypes.c_char),
        ('after_R_rotor_back', ctypes.c_char),
        ('after_plugboard_2', ctypes.c_char),
        ('output_char', ctypes.c_char)
    ]
    
    def __str__(self) -> str:
        return (
            f"Input char:           {self.input_char.decode('utf-8')}\n"
            f"After plugboard 1:    {self.after_plugboard_1.decode('utf-8')}\n"
            f"After R rotor:        {self.after_R_rotor.decode('utf-8')}\n"
            f"After M rotor:        {self.after_M_rotor.decode('utf-8')}\n"
            f"After L rotor:        {self.after_L_rotor.decode('utf-8')}\n"
            f"After reflector:      {self.after_reflector.decode('utf-8')}\n"
            f"After L rotor back:   {self.after_L_rotor_back.decode('utf-8')}\n"
            f"After M rotor back:   {self.after_M_rotor_back.decode('utf-8')}\n"
            f"After R rotor back:   {self.after_R_rotor_back.decode('utf-8')}\n"
            f"After plugboard 2:    {self.after_plugboard_2.decode('utf-8')}\n"
            f"Output char:          {self.output_char.decode('utf-8')}"
        )


class Enigma(Scene):

    def create_rotor(
        self,
        wiring: Wiring,
        outer_radius: float = 1.4,
        inner_radius: float = 1.2,
        font: str = "Iosevka",
        font_size: int = 20,
        letter_color: ManimColor = WHITE,
        orientation: str = "upright",  # upright, radial, tangent
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

        r_mid = 0.5 * (inner_radius + outer_radius)
        r_index = outer_radius + 0.15  # distance of the 0..25 labels from center
        n = len(wiring.value)       # usually 26

        for i, ch in enumerate(wiring.value):
            # angle starts at top (PI/2) and goes clockwise (-i)
            angle = (PI / 2) - i * (PI * 2 / n)

            # position of the letter
            pos_letter = np.array([np.cos(angle), np.sin(angle), 0.0]) * r_mid
            t = Text(ch, font=font, font_size=font_size, weight=BOLD)
            t.set_color(letter_color)
            t.set_stroke(BLACK, width=0.6, opacity=0.7)

            # optional orientation for letters
            if orientation == "radial":
                t.rotate(angle)
            elif orientation == "tangent":
                t.rotate(angle - PI / 2)
            t.move_to(pos_letter)
            letters.add(t)

            # position of the numeric index (always upright)
            pos_index = np.array([np.cos(angle), np.sin(angle), 0.0]) * r_index
            idx = Text(str(i), font=font, font_size=int(font_size * 0.6), weight=BOLD)
            idx.set_color(BLUE)
            idx.set_stroke(BLACK, width=0.6, opacity=0.7)
            idx.move_to(pos_index)
            indices.add(idx)

        # rotor[0] = ring, rotor[1] = highlight, rotor[2] = letters, rotor[3] = indices
        return VGroup(ring, highlight, letters, indices)



    def update_content(
        self,
        current_object,
        new_content,
        content_type="text",
        ):
        """
        function to update the content of a rotor/text object
        """

        if content_type == "text":
            new_object = Text(new_content, font_size=16, font="Iosevka")
            new_object.set_color_by_gradient(RED, BLUE, GREEN)
        elif content_type == "rotor":
            new_object = self.create_rotor(new_content)
        else:
            raise ValueError(f"content_type inesistente: {content_type}")

        new_object.move_to(current_object)
        self.play(Transform(current_object, new_object))
        return current_object

    def construct(self):
        # loading shared library
        try:
            so_file = "build/enigma.so"
            enigma = ctypes.CDLL(so_file)
        except OSError as e:
            print(f"Error loading shared library: {e}")
            return

        # specifying arg and return types of the trace_encrypt function
        trace_encrypt = enigma.trace_encrypt;
        trace_encrypt.restype = EncryptionSteps
        trace_encrypt.argtypes = [ctypes.c_char];

        # calling encrypt(char c)
        print("Type a letter to encrypt (A-Z): ", end="")
        user_input = input().strip().upper()
        steps = trace_encrypt(user_input.encode('utf-8'))
        print(steps)

        # asking if proceeding with video
        print("Animation? (y/n): ", end="")
        proceed = input().strip().lower()

        if proceed != 'y':
            print("Aborting animation..")
            return

        testo = Text("Benvenuto in questo esempio di animazione dell'attraversamento\nin avanti della macchina Enigma M3", font_size=24, font="Iosevka")
        testo.set_color_by_gradient(RED, BLUE, GREEN)
        self.play(Write(testo))
        self.wait(3)
        self.update_content(testo, "Questo visualizzatore utilizza come rotore di destra il rotore III,\ncome rotore di mezzo il rotore II, e come ultimo il rotore I.")
        self.wait(3)
        self.update_content(testo, "L'animazione allo stato attuale non supporta il plugboard, e come riflettore usa il riflettore B")
        self.wait(3)
        self.update_content(testo, "Quando l'utente preme una lettera, i rotori girano, e poi parte il segnale elettrico corrispondente a quella lettera")
        self.wait(3)
        self.remove(testo) 
        
        testo2 = Text("Qui un'immagine di esempio di un rotore:", font_size=16, font="Iosevka")
        testo2.set_color_by_gradient(RED, BLUE, GREEN).shift(UP*2)
        rotor_image = ImageMobject("imgs/cool_rotors.jpg") 
        rotor_image.scale(1.8)

        self.play(Write(testo2))
        self.play(FadeIn(rotor_image), run_time=3)
        self.wait(3)

        # Animate it disappearing before the rest of the visualization starts
        self.play(FadeOut(rotor_image))
        self.play(FadeOut(testo2))

        input_char = steps.input_char.decode('utf-8')
        after_R_rotor = steps.after_R_rotor.decode('utf-8')

        # display text
        t1 = Text(f"""Prendo il rotore III ({Wiring.ROTOR_III.value}) della macchina enigma\n
            nella sua posizione iniziale (parto dall'indice 0)
            """,
            font_size=16, font="Iosevka")
        t1.set_color_by_gradient(RED, BLUE, GREEN)
        t1.shift(UP)
        self.play(Write(t1))
        self.wait(3)

        # display right rotor
        rotor_r: VGroup = self.create_rotor(Wiring.ROTOR_III)
        rotor_r.shift(DOWN)
        self.play(FadeIn(rotor_r))
        self.wait(3)

        # display pressing letter, and stepping mechanism
        self.update_content(t1, f"""
            Ora premo il tasto '{input_char}'.\nIl rotore di destra, avanza sempre di una posizione,\nprima che il segnale elettrico parta
            """, "text")
        self.wait(3) 
        
        input_char_t = Text(input_char, font_size=16, font="Iosevka")
        input_char_t.set_color_by_gradient(RED, ORANGE)
        input_char_t.shift(RIGHT*1.5)
        self.play(Write(input_char_t))
        
        # displayng what happens after stepping
        idx_input = character_alphabet_index(input_char)
        idx_input_stepped = (idx_input + 1) % 26
        char_at_stepped = alphabet_character_at_index(idx_input_stepped)
        self.update_content(t1, f"Questa rotazione sposta il corpo del rotore di 1/26 di giro", "text")
        self.wait(3)

        self.update_content(t1, f"Il risultato è che i cablaggi interni\n non sono più allineati come prima:", "text")
        self.wait(3)
        
        self.update_content(t1, f"L'ingresso '{input_char}'\nnon si connette più al pin '{input_char}'({idx_input}),\nma a quello successivo modulo26,\nil pin '{char_at_stepped}'({idx_input_stepped})", "text")
        self.wait(3)
        
        self.update_content(t1, f"Entra il segnale della lettera '{input_char}' (idx{idx_input}),\nma a causa dello step, il segnale segue\nil percorso del cablaggio che parte dal pin all'indice {idx_input_stepped} ({idx_input} + 1 modulo 26)", "text")
        self.wait(3)

        self.update_content(t1, f"""
            Il cablaggio del Rotore III al nuovo indice {idx_input_stepped} ha la lettera {Wiring.ROTOR_III.value[idx_input_stepped]}
        """, "text")
        self.wait(3)
        
        letter = rotor_r[2][idx_input_stepped].set_color(YELLOW) # rotor_r[2]: letters in VGroup
        self.play(letter.animate.set_color(YELLOW))
        self.wait(3)
        self.play(letter.animate.set_color(WHITE))
        self.wait(3)

        self.update_content(t1, f"Tuttavia anche l'uscita è sfalsata.\nIl segnale esce dal contatto {Wiring.ROTOR_III.value[idx_input_stepped]} (indice {character_alphabet_index(Wiring.ROTOR_III.value[idx_input_stepped])}),\nma siccome tutto il rotore è ruotato, va sottratto l'offset: {character_alphabet_index(Wiring.ROTOR_III.value[idx_input_stepped])} - 1 = {character_alphabet_index(after_R_rotor)}", "text")
        self.wait(3)

        self.update_content(t1, f"L'indice {character_alphabet_index(after_R_rotor)}, alfabeticamente corrisponde alla lettera '{after_R_rotor}'.\nQuindi, a causa di un singolo step, la lettera '{input_char}' è stata trasformata in '{after_R_rotor}'\ninvece che in '{Wiring.ROTOR_III.value[idx_input_stepped]}'.\nIl segnale '{after_R_rotor}' ora prosegue verso il rotore successivo", "text")
        self.wait(3)

        idx = Wiring.ROTOR_III.value.index(after_R_rotor)
        letters = rotor_r[2]
        letter_rotor = letters[idx]
        self.play(
            letter_rotor.animate.set_color(YELLOW),
        )
        self.wait(3)
        
        self.play(Transform(input_char_t, letter_rotor))
        self.wait(3)
        
        """
        MIDDLE ROTOR
        """
        # saving new letter
        self.update_content(
            t1,
            f"La stessa cosa ora succede per i rotori successivi,\n"
              f"ma senza lo step in avanti (a meno che il rotore precedente\n"
              f"non si trovi sulla tacca, il notch).",
            "text"
        )
        self.wait(3)
        self.update_content(
            t1,
            f"""
            Ora prendo il rotore di mezzo (rotore II):
            """,
            "text"
        )

        # removing old rotor and creating new middle rotor
        self.remove(rotor_r, input_char_t)
        after_R_rotor_t = Text(after_R_rotor, font_size=16, font="Iosevka")
        after_R_rotor_t.set_color_by_gradient(RED, ORANGE)
        after_R_rotor_t.shift(RIGHT*1.5)
        self.play(FadeIn(after_R_rotor_t))

        rotor_m = self.create_rotor(Wiring.ROTOR_II)
        rotor_m.shift(DOWN)
        self.play(FadeIn(rotor_m))
        self.wait(3)
        
        # letter enters middle rotor
        after_M_rotor = steps.after_M_rotor.decode('utf-8')
        self.update_content(
            t1,
            f"""
            La lettera '{after_R_rotor}' ha indice alfabetico {character_alphabet_index(after_R_rotor)} e quindi entra
            nella posizione di indice {character_alphabet_index(after_R_rotor)} del rotore, che corrisponde alla lettera
            '{after_M_rotor}' sul rotore.
            """,
            "text"
        )
        self.wait(3)


        idx = character_alphabet_index(after_R_rotor)
        letters = rotor_m[2]
        indices = rotor_m[3]
        letter_rotor = letters[idx]
        index_label = indices[idx]
        self.play(
            letter_rotor.animate.set_color(YELLOW),
            index_label.animate.set_color(YELLOW),
        )
        self.wait(3)
        
        self.play(Transform(after_R_rotor_t, letter_rotor))
        self.wait(3)
        


        """
        LEFT ROTOR
        """
        # saving new letter
        self.update_content(
            t1,
            f"""
            Infine prendo il rotore più a sinistra (rotore I):
            """,
            "text"
        )
       
        # removing old rotor and creating new left rotor
        self.remove(rotor_m, after_R_rotor_t)
        after_M_rotor_t = Text(after_M_rotor, font_size=16, font="Iosevka")
        after_M_rotor_t.set_color_by_gradient(RED, ORANGE)
        after_M_rotor_t.shift(RIGHT*1.5)
        self.play(FadeIn(after_M_rotor_t))

        rotor_l = self.create_rotor(Wiring.ROTOR_I)
        rotor_l.shift(DOWN)
        self.play(FadeIn(rotor_l))
        self.wait(3)
        
        # letter enters left rotor
        after_L_rotor = steps.after_L_rotor.decode('utf-8')
        self.update_content(
            t1,
            f"""
            La lettera '{after_M_rotor}' ha indice alfabetico {character_alphabet_index(after_M_rotor)} e quindi entra
            nella posizione di indice {character_alphabet_index(after_M_rotor)} del rotore, che corrisponde alla lettera
            '{after_L_rotor}' sul rotore.
            """,
            "text"
        )
        self.wait(3)

        idx = character_alphabet_index(after_M_rotor)
        letters = rotor_l[2]
        indices = rotor_l[3]
        letter_rotor = letters[idx]
        index_label = indices[idx]
        self.play(
            letter_rotor.animate.set_color(YELLOW),
            index_label.animate.set_color(YELLOW),
        )
        self.wait(3)
        
        self.play(Transform(after_M_rotor_t, letter_rotor))
        self.wait(3)


        """
        REFLECTOR B
        """
        # saving new letter
        self.update_content(
            t1,
            f"""
            Ora i tre rotori sono stati attraversati, e il segnale giunge al riflettore, in questo caso il riflettore 'B':
            """,
            "text"
        )
       
        # removing old rotor and creating reflector
        self.remove(rotor_l, after_M_rotor_t)
        after_L_rotor_t = Text(after_L_rotor, font_size=16, font="Iosevka")
        after_L_rotor_t.set_color_by_gradient(RED, ORANGE)
        after_L_rotor_t.shift(RIGHT*1.5)
        self.play(FadeIn(after_L_rotor_t))

        reflector = self.create_rotor(Wiring.REFLECTOR_B)
        reflector.shift(DOWN)
        self.play(FadeIn(reflector))
        self.wait(3)
        
        # letter enters reflector
        after_reflector = steps.after_reflector.decode('utf-8')
        self.update_content(
            t1,
            f"""
            Il riflettore ha il semplice compito di invertire il percorso del segnale.
            1) La lettera '{after_L_rotor}' (indice {character_alphabet_index(after_L_rotor)}) entra nel pin corrispondente.
            2) Quel pin è cablato direttamente alla lettera '{after_reflector}'.
            3) Il segnale ora torna indietro nei rotori, partendo dal contatto corrispondente a '{after_reflector}'.
            """,
            "text"
        )
        self.wait(3)

        idx = character_alphabet_index(after_L_rotor)
        letters = reflector[2]
        indices = reflector[3]
        letter_reflector = letters[idx]
        index_label = indices[idx]
        self.play(
            letter_reflector.animate.set_color(YELLOW),
            index_label.animate.set_color(YELLOW),
        )
        self.wait(3)

        self.play(Transform(after_L_rotor_t, letter_reflector))
        self.wait(3)

        # ritorno attraverso i rotori e plugboard, fino alla lampadina finale
        self.remove(reflector, after_L_rotor_t)

        output_char = steps.output_char.decode('utf-8')
        self.update_content(
            t1,
            "Una volta uscito dal riflettore, il segnale attraversa di nuovo i tre rotori in senso inverso,\n"
            "passando prima dal rotore I, poi dal rotore II e infine dal rotore III,\nseguendo gli stessi cablaggi ma al contrario.",
            "text"
        )
        self.wait(3)

        self.update_content(
            t1,
            f"Dopo l'ultimo passaggio nel plugboard, il segnale arriva al pannello delle lampadine,\naccende la lampadina corrispondente alla lettera cifrata finale, che in questo caso è '{output_char}'.",
            "text"
        )
        self.wait(3)

