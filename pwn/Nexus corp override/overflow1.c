#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void unlock_credentials()
{
    FILE *fp = fopen("flag.txt", "r");
    if (!fp) {
        perror("Could not open flag.txt");
        exit(1);
    }
    char flag[100];
    fgets(flag, sizeof(flag), fp);
    fclose(fp);
    printf("CREDENTIALS UNLOCKED: %s\n", flag);
    fflush(stdout);
}

void authenticate_user()
{
    char employee_id[24];
    int clearance_level = 0;
    
    printf("=== NEXUS CORP SECURITY TERMINAL ===\n");
fflush(stdout);
    printf("Enter your employee ID:\n");
fflush(stdout);
    gets(employee_id);
    
    printf("Welcome, %s!\n", employee_id);
    
    if (clearance_level == 0x1337) {
        printf("HIGH CLEARANCE DETECTED. Unlocking admin credentials...\n");
        unlock_credentials();
    } else {
        printf("INSUFFICIENT CLEARANCE. Access restricted to public areas.\n");
    }
}

int main()
{
    authenticate_user();
    return 0;
}
