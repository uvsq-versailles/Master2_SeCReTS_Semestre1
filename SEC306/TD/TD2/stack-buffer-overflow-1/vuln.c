/**
 * gcc -Wall -m32 -fno-stack-protector -mpreferred-stack-boundary=2 vuln.c
 * 
 * -m32 : pour un environnement m32
 * -fno-stack-protector : proteger la stack
 * -mpreferred-stack-boundary=2
 **/
 
 // 

#include <stdio.h>
#define TAILLE_MAXIMUM_PRENOM 64

void ask_me_im_famous()
{
    char prenom[TAILLE_MAXIMUM_PRENOM];
    gets(prenom);
}

int main(int argc, char** argv, char** envp)
{
    puts("Tapez votre prénom :");
    ask_me_im_famous();
    puts("Bonjour !");

    return 0;
}

