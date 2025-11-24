/* Enigma M3 Simulator */

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* --------- constants + macros */
#define ALPHABET_SIZE 26
#define NUM_ROTORS 3

#define INDEX_TO_C(index) ((char) ('A' + (index)))
#define C_TO_INDEX(c)     ((int)  ((c) - 'A'))

static inline int 
mod26 (int x)
{
    /* (.. + 26) % 26 is needed to guarantee a result in [0-25] */
    return (x % 26 + 26) % 26;
}

/* rotor direction */
enum { RIGHT = 0, MIDDLE = 1, LEFT = 2 };

/* --------- structs & vars */
typedef char Wiring[ALPHABET_SIZE];

typedef struct {
    Wiring wiring;
    const char *name;
} Reflector;

typedef struct {
    Wiring wiring;
    char notch;
    int position;
    int ring_setting;
    const char *name;
} Rotor;

typedef struct {
    char wiring[ALPHABET_SIZE]; 
} Plugboard;

/* struct to keep track of each step during encryption, for manim animation */
typedef struct {
    char input_char;
    char after_plugboard_1;
    char after_R_rotor;
    char after_M_rotor; 
    char after_L_rotor;
    char after_reflector;
    char after_L_rotor_back;
    char after_M_rotor_back; 
    char after_R_rotor_back;
    char after_plugboard_2;
    char output_char;
} EncryptionSteps;

typedef struct {
    Rotor rotors[NUM_ROTORS];
    Reflector reflector;
    Plugboard plugboard;
} Enigma;

// https://www.ciphermachinesandcryptology.com/en/enigmatech.htm
static const Reflector ALL_REFLECTORS[] = {
    { .wiring = "YRUHQSLDPXNGOKMIEBFZCWVJAT", .name = "Reflector B" },
    { .wiring = "FVPJIAOYEDRZXWGCTKUQSBNMHL", .name = "Reflector C" }
};

// https://www.codesandciphers.org.uk/enigma/rotorspec.htm
static const Rotor ALL_ROTORS[] = {
    /* 
     * a ring setting of 0 is identical to A (A0, B1, .. , Z25)
     * position can be A0, B1, .. , Z25 
    */
    { .wiring = "EKMFLGDQVZNTOWYHXUSPAIBRCJ", .notch = 'Q', .position = 0, .ring_setting = 0, .name = "Rotor I" },
    { .wiring = "AJDKSIRUXBLHWTMCQGZNPYFVOE", .notch = 'E', .position = 0, .ring_setting = 0, .name = "Rotor II" },
    { .wiring = "BDFHJLCPRTXVZNYEIWGAKMUSQO", .notch = 'V', .position = 0, .ring_setting = 0, .name = "Rotor III" },
    { .wiring = "ESOVPZJAYQUIRHXLNFTGKDCMWB", .notch = 'J', .position = 0, .ring_setting = 0, .name = "Rotor IV"},
    { .wiring = "VZBRGITYUPSDNHLXAWMJQOFECK", .notch = 'Z', .position = 0, .ring_setting = 0, .name = "Rotor V"}
    /*{ .wiring = "JPGVOUMFYQBENHZRDKASXLICTW", .notch = '', .position = 0, .name = "Rotor VI"}
      { .wiring = "NZJHGRCXMYSWBOUFAIVLPEKQDT", .notch = '', .position = 0, .name = "Rotor VII"}
      { .wiring = "FKQHTLXOCBJSPDZRAMEWNIUYGV", .notch = '', .position = 0, .name = "Rotor VIII"}*/
};

static const Plugboard PLUGBOARD_CONFIGS[] = {
    { .wiring = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" }, // no connections
    { .wiring = "ABQDEFGHIJKLMNOPCRSTUVWXYZ" }  // Q swapped with C
};

/* --------- functions */

static char 
rotor_forward (char c, const Rotor *r)
{
    int index = mod26(C_TO_INDEX(c) + r->position - r->ring_setting);
    char wired = r->wiring[index];
    return INDEX_TO_C(mod26(C_TO_INDEX(wired) - r->position + r->ring_setting));
}

static char 
rotor_backward (char c, const Rotor *r) 
{
    int shifted_c = mod26(C_TO_INDEX(c) + r->position - r->ring_setting);
    int inverse_index = 0;
    
    for (int i = 0; i < ALPHABET_SIZE; i++) {
        if (r->wiring[i] == INDEX_TO_C(shifted_c)) {
            inverse_index = i;
            break;
        }
    }
    return INDEX_TO_C(mod26(inverse_index - r->position + r->ring_setting));
}

static void 
print_status (const Rotor rotors[])
{
    int i, j;
    printf("\n=====STATUS=====\n");
    for (i = 0; i < NUM_ROTORS; i++){
        printf("Name: %s:\n", rotors[i].name);
        printf("Wiring: ");
        for(j = 0; j < ALPHABET_SIZE; j++)
            printf("%c", rotors[i].wiring[j]);
        
        printf("\nPosition: %d (%c)\n", rotors[i].position, INDEX_TO_C(rotors[i].position));
        printf("Ring setting: %d (%c)\n", rotors[i].ring_setting, INDEX_TO_C(rotors[i].ring_setting));
        printf("Notch: %c\n", rotors[i].notch);
        printf("--------------------\n");
    }
    printf("=======END=======\n\n");
}

static char 
encrypt_character (char c, const Enigma *e)
{
    for (int i = 0; i < NUM_ROTORS; i++){
        c = rotor_forward(c, &e->rotors[i]);
    } 
    
    c = e->reflector.wiring[C_TO_INDEX(c)];
    
    for (int i = NUM_ROTORS - 1; i >= 0; i--){
        c = rotor_backward(c, &e->rotors[i]);
    }

    return c;
}

static void
step_rotors(Enigma *e)
{
    Rotor *r = e->rotors;

    /* there is not ring setting because it does not interfere with stepping mechanism */
    bool right_is_at_notch  = (C_TO_INDEX(r[RIGHT].notch)  == r[RIGHT].position);
    bool middle_is_at_notch = (C_TO_INDEX(r[MIDDLE].notch) == r[MIDDLE].position);
    
    // double step ( se middle su notch, avanza anche left)
    if (middle_is_at_notch)
        r[LEFT].position = (r[LEFT].position + 1) % ALPHABET_SIZE;

    // middle avanza se right su notch oppure middle su notch
    if (right_is_at_notch || middle_is_at_notch)
        r[MIDDLE].position = (r[MIDDLE].position + 1) % ALPHABET_SIZE;
    
    // right avanza sempre
    r[RIGHT].position = (r[RIGHT].position + 1) % ALPHABET_SIZE;
}

static char 
enter_plugboard (char c, const Enigma *e)
{
    for (int i = 0; i < ALPHABET_SIZE; i++){
        if (c == e->plugboard.wiring[i])
            return INDEX_TO_C(i);
    }
    return c;
}

static void 
choose_rotors (Rotor rotors[]) 
{
    int choice;
    int n_available_rotors = (int) (sizeof(ALL_ROTORS) / sizeof(ALL_ROTORS[0]));
    const char *side_names[NUM_ROTORS] = { "right", "middle", "left" };
    
    printf("Available rotors:\n");
    for (int i = 0; i < n_available_rotors; i++){
        printf("%d: %s\n", i + 1, ALL_ROTORS[i].name);
    }
    printf("\n");
    
    /* loop for choosing settings for every rotors */
    for (int i = 0; i < NUM_ROTORS; i++){
        
        /* choose which rotor */
        printf("Choose the %s rotor (1-%d): ", side_names[i], n_available_rotors);
        if (scanf("%d", &choice) != 1 || choice < 1 || choice > n_available_rotors){
            printf("rotor invalid, default to rotor %d\n", 3-i);
            choice = 3-i;
        }
        rotors[i] = ALL_ROTORS[choice - 1];
        
        /* starting position */
        int position;
        printf("  Starting position for %s rotor (0-25): ", side_names[i]);
        scanf("%d", &position);
        if (position < 0 || position > 25) {
            printf("Invalid position. Defaulting to 0 (A).\n");
            rotors[i].position = 0;
        } else {
            rotors[i].position = position;
        }

        /* ring setting */
        int ring_setting;
        printf("  Ring setting for %s rotor (0-25): ", side_names[i]);
        scanf("%d", &ring_setting);
        if (ring_setting < 0 || ring_setting > 25) {
            printf("Invalid ring setting. Defaulting to 0 (A).\n");
            rotors[i].ring_setting = 0;
        } else {
            rotors[i].ring_setting = ring_setting;
        }
    }

    int ch;
    while ((ch = getchar()) != '\n' && ch != EOF);
}

static void
choose_plugboard (Plugboard *plugboard)
{
    int choice;

    printf("Choose the plugboard:\n\n");
    printf("Available plugboard configurations:\n");
    printf("1: no connections:\n");
    printf("2: Q swapped with C");
    printf("\n");

    printf("Choose plugboard (1-%zu): ", sizeof(PLUGBOARD_CONFIGS) / sizeof(PLUGBOARD_CONFIGS[0]));
    scanf("%d", &choice);

    if (choice < 1 || choice > (int) (sizeof(PLUGBOARD_CONFIGS) / sizeof(PLUGBOARD_CONFIGS[0]))) {
        printf("Invalid choice. Default is plugboard 1 (no connections).\n");
        *plugboard = PLUGBOARD_CONFIGS[0];
    } else {
        *plugboard = PLUGBOARD_CONFIGS[choice - 1];
    }

    int ch;
    while ((ch = getchar()) != '\n' && ch != EOF);
}

static void
choose_reflector(Reflector *reflector)
{
    int choice;

    printf("Available reflectors:\n");
    printf("1: %s\n", ALL_REFLECTORS[0].name);
    printf("2: %s\n", ALL_REFLECTORS[1].name);
    printf("\n");

    printf("Choose the reflector (1-2): ");
    if (scanf("%d", &choice) != 1) {
        printf("Invalid input. Default is Reflector B.\n");
        *reflector = ALL_REFLECTORS[0];
    } else if (choice == 1) {
        *reflector = ALL_REFLECTORS[0];
    } else if (choice == 2) {
        *reflector = ALL_REFLECTORS[1];
    } else {
        printf("Invalid choice. Default is Reflector B.\n");
        *reflector = ALL_REFLECTORS[0];
    }
    
    printf("Selected %s.\n", reflector->name);
    int ch;
    while ((ch = getchar()) != '\n' && ch != EOF);
}

/* used for manim animation */
EncryptionSteps 
trace_encrypt(char c)
{
    EncryptionSteps steps;
    Enigma e = {
        .plugboard      = PLUGBOARD_CONFIGS[0],
        .reflector      = ALL_REFLECTORS[0],
        .rotors[RIGHT]  = ALL_ROTORS[2],
        .rotors[MIDDLE] = ALL_ROTORS[1],
        .rotors[LEFT]   = ALL_ROTORS[0]
    };
    
    steps.input_char = c;

    /* prima di cifrare, fare lo step dei rotori */
    step_rotors(&e);

    /* plugboard in ingresso */
    c = enter_plugboard(c, &e);
    steps.after_plugboard_1 = c;

    /* andata nei tre rotori */
    c = rotor_forward(c, &e.rotors[RIGHT]);
    steps.after_R_rotor = c;
    c = rotor_forward(c, &e.rotors[MIDDLE]);
    steps.after_M_rotor = c;
    c = rotor_forward(c, &e.rotors[LEFT]);
    steps.after_L_rotor = c;

    /* riflettore */
    c = e.reflector.wiring[C_TO_INDEX(c)];
    steps.after_reflector = c;

    /* ritorno nei tre rotori */
    c = rotor_backward(c, &e.rotors[LEFT]);
    steps.after_L_rotor_back = c;
    c = rotor_backward(c, &e.rotors[MIDDLE]);
    steps.after_M_rotor_back = c;
    c = rotor_backward(c, &e.rotors[RIGHT]);
    steps.after_R_rotor_back = c;
    
    /* plugboard in uscita */
    c = enter_plugboard(c, &e);
    steps.after_plugboard_2 = c;

    steps.output_char = c;
    return steps;
}
    
void 
encrypt_word (Enigma *e, const char *word, char *encrypted_word)
{
    size_t i;
	for (i = 0; word[i] != '\0'; i++) {
		printf("encrypting character: %c\n", word[i]);

        /* step rotors */
        printf("Stepping rotors...\n");
        step_rotors(e);
        print_status(e->rotors);
        
        /* enter the plugboard */
        char c = enter_plugboard(word[i], e);
        printf("Character after plugboard (in): %c\n", c);
        
        /* go through rotors, reflector and rotors */
        char encrypted_char = encrypt_character(c, e);
        
        /* enter the plugboard */
        encrypted_char = enter_plugboard(encrypted_char, e);
        printf("encrypted character: %c -> %c\n", c, encrypted_char);

        encrypted_word[i] = encrypted_char;
	}

    encrypted_word[i] = '\0';
}


int 
main (void) 
{
    Enigma e;
    
    /* generated using figlet.org */
    printf(" _____       _                             __  __ _____\n");
    printf("| ____|_ __ (_) __ _ _ __ ___   __ _      |  \\/  |___ /\n");
    printf("|  _| | '_ \\| |/ _` | '_ ` _ \\ / _` |_____| |\\/| | |_ \\\n");
    printf("| |___| | | | | (_| | | | | | | (_| |_____| |  | |___) |\n");
    printf("|_____|_| |_|_|\\__, |_| |_| |_|\\__,_|     |_|  |_|____/\n");
    printf("               |___/                                   \n");
    
    choose_plugboard(&e.plugboard);
    choose_reflector(&e.reflector);
    choose_rotors(e.rotors);
    
    print_status(e.rotors);
       
    printf("Enter word to encrypt: (only uppercase letters, no spaces)\n");
    char word[1024];
    if (! fgets(word, sizeof(word), stdin)){
        perror("error reading input string to encrypt");
        return 1;
    }
    
    /* removing '\n' from word */
    size_t len = strlen(word);
    if (len > 0 && word[len - 1] == '\n') {
        word[len - 1] = '\0';
        len--;
    }

    /* allocating buffer for encrypted string */
    char *encrypted_word = malloc(len + 1);
    if (! encrypted_word) {
        perror("error allocating memory for encrypted buffer");
        return 1;
    }
    
    encrypt_word(&e, word, encrypted_word);
    printf("\nEncrypted word: %s\n", encrypted_word);
    
    free(encrypted_word);
    return 0;
}
