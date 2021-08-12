#include <stdio.h>
#include <string.h>
#include <unistd.h>

/* Copyright (C) 2021 HITB SECCONF CTF - All Rights Reserved
 * You may use, distribute and modify this code under the
 * terms of the CTF license, which unfortunately won't be
 * written for another century.
 */

int main()
{
    char flag[] = "%FLAG%";
    for (unsigned short int i = 0; i < strlen(flag); i++) {
        int key;
        scanf("%d", &key);
        printf("%d ", flag[i] ^ key);
        usleep(100000);
    }
    return 0;
}