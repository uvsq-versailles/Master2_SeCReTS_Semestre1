# reverse-engineering

Nous allons faire du reverse engineering. Pour cela, nous ferons la liste des registres et des instructions importantes puis l'étude de l'assembleur à l'aide d'un exemple. 

## Registres

### Registres de travaux

- **EAX** : registre accumulateur (accumulator register). Utilisé pour les opérations arithmétiques et le stockage de la valeur de retour des appels systèmes.
- **EDX** : registre de données (data register). Utilisé pour les opérations arithmétiques et les opérations d'entrée/sortie.
- **ECX** : registre compteur (counter register)
- **EBX** : registre de base (base register). Utilisé comme pointeur de donnée (située dans DS en mode segmenté).

Ce sont des registres 32 bits. Pour des raisons historiques, les 16 bits de poids faible sont constitués respectivement des registres **AX**, **DX**, **CX** et **BX**. 
Pour les architectures 64 bits, ils correspondent à **RAX**, **RDX**, **RCX** et **RBX** et font 64 bits. 
On accède aux 32 bits moins significatifs en utilisant les noms originels **EAX**, **EBX**, **ECX**, **EDX**.

Ces 4 registres 16 bits (**EAX**, **EBX**, **ECX**, **EDX**) sont également décomposés en 8 registres de 8 bits :

- **AL** : octet de poids faible de **AX**
- **AH** : octet de poids fort de **AX**
- **BL** : octet de poids faible de **BX**
- **BH** : octet de poids fort de **BX**
- **CL** : octet de poids faible de **CX**
- **CH** : octet de poids fort de **CX**
- **DL** : octet de poids faible de **DX**
- **DH** : octet de poids fort de **DX**

### Registres d'offset

Les registres d'offset sont utilisés lors de l'adressage indirect de la mémoire (pointeurs). Ces registres complémentaires sont :

- **EBP** : (Extended Base Pointer) pointeur du bas de la pile
- **ESP** : (Extended Stack Pointer) pointeur du haut de la pile
- **EIP** : instruction de la prochaine instruction à exécuter

## Instructions importantes

Une instruction (Intel) se compose de 3 mots : ```OPERATION DESTINATION, SOURCE```. Sur AT&T, l'ordre change : ```OPERATION SOURCE, DESTINATION```.

- **SUB** : permet de soustraire une valeur à une autre

```SUB eax, 42    ; eax = eax - 42```

- **ADD** : permet d’additionner deux valeurs

```ADD eax, 42    ; eax = eax + 42```

- **AND** : effectue un ET logique

```AND 0x5, 0x3    ; 5 XOR 3 donne 1 mais stocké nul part (AND utile si on met un registre en paramètre)```

- **XOR** : effectue un XOR logique. Souvent utilisé pour mettre une variable à 0 car X XOR X = 0

```XOR eax, eax```

- **MOV** : assigne une valeur à une variable

```MOV eax, 0x00000042    ; le registre eax va contenir 0x00000042```

- **LEA** : assigne l’adresse d’une variable à une variable. LEA a une particularité, c’est que le deuxième argument est entre crochets, mais contrairement à d’habitude, cela ne veut pas dire qu’il sera déréférencé (c’est à dire que ça ne signifie pas que le résultat sera la variable située à l’adresse entre crochets)

```LEA eax, [ebp - 0xc]    ; charge l'adresse de ebp - 0xc dans eax```

- **PUSH** : pousse l’argument passé à PUSH au sommet de la pile

```PUSH ebp    ; la valeur de ebp est mis sur le dessus de la pile```

- **POP** : retire l’élément au sommet de la pile, et l’assigne à la valeur passée en argument. (Si nous voulons être plus exacts, l’élément au sommet de la pile reste là où il est, et le registre ESP qui pointe sur le sommet de la pile est mis à jour en pointant vers la valeur précédente sur la pile)

```POP ebp    ; l'élément qui était au sommet de la pile est assigné à EBP, et est retiré de la pile```

- **CMP** : compare les deux valeurs passées en argument. C'est le registre des indicateurs qui contient les résultats de la comparaison. Ni Source ni Destination ne sont modifiés

```CMP ecx, 0x10    ; on utilise les sauts conditionnels juste après cette instruction pour utiliser cette comparaison```

- **TEST** : effectue un AND

```TEST EAX, EAX    ; equivalent à cmp eax, 0```

- **JMP** : saut quelque soit la condition

```JMP 0x80844264```

JMP 0x80844264

qui va sauter à l’instruction située à l’adresse indiquée, quoiqu’il arrive.

Cependant, il existe de multiple sauts conditionnels. Nous n’allons pas tous les voir en détails ici, seulement ceux que nous retrouvons le plus. Ils seront présentés par paire, la condition et sa négation, représentée par un N (Not)

- **JE** - **JNE** : egal - différent 
```
CMP ecx, 0x10
JNE else           ; si pas égal,  on saute à else
MOV BX, 5          ; sinon on est dans le then
JMP endif          ; on saute le then pour aller à la fin du if
else:
MOV BX, DX
endif:
```

- **JZ** - **JNZ** : nul - non null

- **JA**/**JB** - **JNA**/**JNB** : supérieur strictement (Above)/inférieur strictement (Below) - inférieur ou égal/supérieur ou égal

- **JG**/**JL** : supérieur (Greater)/ inférieur (Lower)


- **CALL** : permet de faire appel au code d’une autre fonction située à un espace mémoire différent. L’adresse qui lui est passée en argument permet de trouver ce code. Cet appel est en fait un condensé de deux instructions. La première permet de sauvegarder l’instruction qui suit le call (pour le retour de la fonction, afin de reprendre le fil d’exécution du programme) et la deuxième permet d’effectivement sauter à la fonction recherchée. Le registre qui contient l’instruction suivante est EIP

```
CALL 0x80483dc

; equivalent

PUSH EIP
JMP 0x80483dc
```

- **LEAVE** : permet de préparer la sortie d’une fonction en récupérant les variables enregistrée lors du début de la fonction afin de retrouver le contexte d’exécution tel qu’il avait été enregistré juste avant d’exécuter le code de la fonction, tout détruisant ce qu’il restait du stackframe

```
LEAVE

; equivalent

MOV esp, ebp
POP ebp
```

- **RET** : permet de finaliser le travail de LEAVE en récupérant l’adresse de l’instruction à exécuter après le call, adresse qui avait été enregistrée sur la pile lors de l’instruction CALL, et de sauter à cette adresse

```
RET

; equivalent

POP eip
```

- **NOP** : permet de ne rien faire et de perdre un cycle

## Exemple concret 

```
; function main:
0x080483f2 <+0>:     push   ebp
0x080483f3 <+1>:     mov    ebp,esp
0x080483f5 <+3>:     sub    esp,0x18
0x080483f8 <+6>:     mov    DWORD PTR [esp+0x4],0x2
0x08048400 <+14>:    mov    DWORD PTR [esp],0x28
0x08048407 <+21>:    call   0x80483dc <add>
0x0804840c <+26>:    mov    DWORD PTR [ebp-0x4],eax
0x0804840f <+29>:    mov    eax,DWORD PTR [ebp-0x4]
0x08048412 <+32>:    leave  
0x08048413 <+33>:    ret 

; function add
0x080483dc <+0>:     push   ebp
0x080483dd <+1>:     mov    ebp,esp
0x080483df <+3>:     sub    esp,0x10
0x080483e2 <+6>:     mov    eax,DWORD PTR [ebp+0xc]
0x080483e5 <+9>:     mov    edx,DWORD PTR [ebp+0x8]
0x080483e8 <+12>:    add    eax,edx
0x080483ea <+14>:    mov    DWORD PTR [ebp-0x4],eax
0x080483ed <+17>:    mov    eax,DWORD PTR [ebp-0x4]
0x080483f0 <+20>:    leave  
0x080483f1 <+21>:    ret
```
### Description de chaque ligne de l'exemple

- ```0x080483f2 <+0>:     push   ebp```

Cette instruction pousse le rregistre EBP sur la pile. Pour rappel, EBP est le registre qui contient l'adresse du début du stack frame de la fonction courante. Comme nous entrons dans une fonction, il faut sauvegarder le début du stackframe de la fonction précédente.

- ```0x080483f3 <+1>:     mov    ebp,esp```

On donne à EBP de la stack frame actuelle ESP (qui est le haut de la stack frame précédente). Maintenant, EBP représente le bas de la stack frame actuelle (de la fonction actuelle).

- ```0x080483f5 <+3>:     sub    esp,0x18```

0x18 représente 24 en décimal. On va allouer 24 octets pour les variables locales de la fonction *main* (on soustrait car les adresses de la pile se décrémentent en montant sur la pile).

- 
```
0x080483f8 <+6>:     mov    DWORD PTR [esp+0x4],0x2
0x08048400 <+14>:    mov    DWORD PTR [esp],0x28
```

On met (0x2=)2 sur la pile et (0x28=)40 également (2 puis 40).

- ```0x08048407 <+21>:    call   0x80483dc <add>```

On appelle la fonction add : ici, on pousse EIP pour se souvenir de là où il faudra continuer (donc il pointe sur l'instruction qui suit celle de call).

- 
```
0x080483dc <+0>:     push   ebp
0x080483dd <+1>:     mov    ebp,esp
0x080483df <+3>:     sub    esp,0x10
```

On prépare la fonction *call* et on réserve pour de l'espace pour les variables locales.

- ```0x080483e2 <+6>:     mov    eax,DWORD PTR [ebp+0xc]```

Cette instruction permet de retrouver le premier paramètre de la première partie de la fonction et met la variable 2 dans EAX.

- ```0x080483e5 <+9>:     mov    edx,DWORD PTR [ebp+0x8]```

Cette instruction permet de retrouver le deuxième paramètre de la deuxième partie de la fonction et met la variable 40 dans EDX.
Donc pour accéder aux arguments de *call*, il faut aller chercher ces derniers dans la stack frame inférieur. D'où **[ebp+0xX]**

- ```0x080483e8 <+12>:    add    eax,edx```

Cette instruction va additionner le contenu des deux registres et va mettre 42 dans EAX (40+2=42).

- ```0x080483ea <+14>:    mov    DWORD PTR [ebp-0x4],eax```

Cette ligne va sauvegarder le résultat du calcul en case *ebp-0x4* qui est la première case libre de la stackframe.

- ```0x080483ed <+17>:    mov    eax,DWORD PTR [ebp-0x4]```

Cette instruction récupère la valeur et la met dans EAX car EAX est le registre utilisé pour le résultat d'une fonction que l'on veut retourner.

-
```
0x080483f0 <+20>:    leave  
0x080483f1 <+21>:    ret
```
Ces instructions permettent de retrouver l'état des registres

- ```0x0804840c <+26>:    mov    DWORD PTR [ebp-0x4],eax```

On va mettre dans DWORD PTR[ebp-0x4] le résultat de la fonction add (soit 40).

- ```0x0804840f <+29>:    mov    eax,DWORD PTR [ebp-0x4]```

EAX donne 40.

-
```
0x08048412 <+32>:    leave  
0x08048413 <+33>:    ret 
```

On quitte la fonction main

### Résultat

```
##include <stdio.h>
int add(int a, int b)
{
    int result = a + b;
    return result;
}

int main(int argc)
{
    int answer;
    answer = add(40, 2);
    return answer;
}

```




