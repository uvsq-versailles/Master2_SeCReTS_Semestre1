# chroot-jail

Une chroot jail permet d'isoler l'exécution d'un programme et d'éviter ainsi la compromission complète d'un système lors de l'exploitation d'une faille. Si un pirate utilise une faille présente sur l'application chrootée, il n'aura accès qu'à l'environnement isolé et non pas à l'ensemble du système d'exploitation. Cela permet donc de limiter les dégâts qu'il pourrait causer. Cet environnement est appelé un chroot jail en anglais, littéralement une prison. 

Pour construire la cage, il faut déterminer et créer une arborescence en conséquence : 
- les binaires utiles pour l'environnement isolé
- leurs bibliothèques qui leur sont dynamiquement liées
- le fichier */etc/passwd* qui permettra de voir les comptes de l'environnement (mais surtout pas le fichier */etc/shadow* qui contient le nom des comptes associés à leurs mots de passe)

```
/
bin
dev
etc
lib
lib64
var
```
Pour trouver toutes ces informations, on utilise *which* pour connaîtrela localisation du binaire demandé et *ldd [path_bin]* pour connaître les bibliothèques dynamiques associées.

## chroot-jail avec thttpd

En lançant la commande, ```chroot . bin/thttpd -D -u root -c '**.sh' -nor```, on déclenche le démon thttpd et sur un navigateur, on peut maintenant être dans la chroot jail automatiquement.

## chroot-jail avec ssh

Prenons deux VM connectées sur le même réseau interne avec 10.0.0.1/24 pour *VMServer* et 10.0.0.2/24 pour *VMClient*. 
Créons un nouvel utilisateur sur *VMServer* user/user. Créons également notre chroot-jail sur ```/home/user/Desktop/chroot-jail```.
Modifions le fichier ```/etc/ssh/sshd_config``` : 

```
Match User user
ChrootDirectory /home/user/Desktop/chroot-jail
```
Puis on reboot. Enfin, activons SSH avec ```sudo systectl start ssh```

Maintenant sur *VMClient*, on fait ```ssh user@10.0.0.1```. Désormais, l'utilisateur est dans la chroot-jail.

