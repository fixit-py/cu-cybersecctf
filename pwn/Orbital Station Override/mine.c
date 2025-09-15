#include <stdio.h>
#include <string.h>
#include <stdbool.h>

void launch_sequence() {
    printf("Access granted! Launching escape pod with classified data!\n");
    fflush(stdout); // Ensure output is flushed
    FILE *flag_file = fopen("flag.txt", "r");
    if (flag_file != NULL) {
        char flag_content[100];
        while (fgets(flag_content, sizeof(flag_content), flag_file) != NULL) {
            printf("%s", flag_content);
            fflush(stdout); // Ensure output is flushed
        }
        fclose(flag_file);
        printf("\n");
        fflush(stdout); // Ensure output is flushed
    } else {
        printf("flag.txt file not found\n");
        fflush(stdout); // Ensure output is flushed
    }
}

void memory_scan(void *addr, int len) {
    int i;
    unsigned char *pc = (unsigned char*)addr;

    for (i = 0; i < len; i++) {
        if ((i % 16) == 0) {
            if (i != 0)
                printf("  ");
            for (int j = i - 16; j < i; j++) {
                if (j >= 0 && j < len) {
                    printf("%c", (pc[j] >= 32 && pc[j] <= 126) ? pc[j] : '.');
                }
            }
            printf("\n");
            printf("%04x ", i);
        }
        printf(" %02x", pc[i]);
    }

    // Print the final ASCII representation for the last line
    int remainder = i % 16;
    if (remainder != 0) {
        for (int j = 0; j < 16 - remainder; j++) {
            printf("   ");
        }
        printf("  ");
        for (int j = i - remainder; j < i; j++) {
            printf("%c", (pc[j] >= 32 && pc[j] <= 126) ? pc[j] : '.');
        }
    }
    printf("\n");
}

int main() {
    struct {
        char databank[64];
        int guardian;
        bool clearance;
    } terminal;
    char buffer[256];

    terminal.guardian = 0x44524942; //BIRD in little endian
    terminal.clearance = false; //set this bool to false

    printf("Welcome to the orbital research station security terminal. Access to classified data requires proper authorization!\n\n");
    fflush(stdout); // Ensure output is flushed

    // Zero out the buffer
    memset(terminal.databank, 0, sizeof(terminal.databank));

    printf("System memory scan before input:");
    fflush(stdout); // Ensure output is flushed
    memory_scan(&terminal, sizeof(terminal));

    printf("\n");
    fflush(stdout); // Ensure output is flushed

    while(1)
    {
        printf("Enter your authorization code: ");
        fflush(stdout); // Ensure output is flushed
        extern char *gets(char *); // Explicit declaration of gets to allow compilation
        gets(terminal.databank);

        printf("\nSystem memory scan after input:");
        fflush(stdout); // Ensure output is flushed
        memory_scan(&terminal, sizeof(terminal));

        if (terminal.guardian != 0x44524942) { // "BIRD" in little-endian
            printf("Security breach detected! Emergency lockdown initiated!\n\n");
            fflush(stdout); // Ensure output is flushed
            return 0;
        } else {
            printf("Security guardian intact.\n");
            fflush(stdout); // Ensure output is flushed
            if (terminal.clearance) {
                launch_sequence();
            } else {
                printf("Authorization insufficient for classified data access...\n\n");
                fflush(stdout); // Ensure output is flushed
            }
        }
    }
}
