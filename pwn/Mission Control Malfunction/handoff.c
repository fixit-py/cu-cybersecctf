#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#define MAX_ENTRIES 10
#define NAME_LEN 32
#define MSG_LEN 64
typedef struct entry {
        char name[8];
        char msg[64];
} entry_t;
void print_menu() {
        puts("What mission operation would you like to perform?");
        puts("1. Add a new crew member");
        puts("2. Send a transmission to crew member");
        puts("3. Exit mission control");
}
int vuln() {
        char feedback[8];
        entry_t entries[10];
        int total_entries = 0;
        int choice = -1;
        // Have a menu that allows the user to write whatever they want to a set buffer elsewhere in memory
        while (true) {
                print_menu();
                if (scanf("%d", &choice) != 1) exit(0);
                getchar(); // Remove trailing \n
                // Add entry
                if (choice == 1) {
                        choice = -1;
                        // Check for max entries
                        if (total_entries >= MAX_ENTRIES) {
                                puts("Maximum crew capacity reached!");
                                continue;
                        }
                        // Add a new entry
                        puts("What's the new crew member's callsign: ");
                        fflush(stdin);
                        fgets(entries[total_entries].name, NAME_LEN, stdin);
                        total_entries++;
                }
                // Add message
                else if (choice == 2) {
                        choice = -1;
                        puts("Which crew member would you like to send a transmission to?");
                        if (scanf("%d", &choice) != 1) exit(0);
                        getchar();
                        if (choice >= total_entries) {
                                puts("Invalid crew member number");
                                continue;
                        }
                        puts("What transmission would you like to send them?");
                        fgets(entries[choice].msg, MSG_LEN, stdin);
                }
                else if (choice == 3) {
                        choice = -1;
                        puts("Thank you for using mission control! If you could take a second to write a quick mission report, we would really appreciate it: ");
                        fgets(feedback, NAME_LEN, stdin);
                        feedback[7] = '\0';
                        break;
                }
                else {
                        choice = -1;
                        puts("Invalid operation");
                }
        }
}
int main() {
        setvbuf(stdout, NULL, _IONBF, 0);  // No buffering (immediate output)
        vuln();
        return 0;
}
