# IPSec

## Creation de l'architecture

Nous aurons besoin de 4 VM : *client1*, *gateway1*, *gateway2*, *client2*.

<img src="/doc/configuration.PNG">

Nous ferons donc la configuration du réseau en donnant l'exemple de la configuration de *client1* et *gateway1*.

### Exemples

#### Configuration de *client1*

On édite le fichier /etc/systemd/network/enp0s3.network : 

```
[Match]
Name=enp0s3

[Network]
Address=10.1.1.2/24
Gateway=10.1.1.1
```

On met à jour les configurations réseaux avec ```$ systemctl restart systemd-networkd```

##### Configuration de *gateway1*

On édite le fichier /etc/systemd/network/enp0s3.network : 

```
[Match]
Name=enp0s3

[Network]
Address=10.1.1.1/24
```

Si on voulait que *gateway1* soit connectée à Internet, il faudrait configurer le fichier comme cela : 

```
[Match]
Name=enp0s3

[Network]
DHCP=ipv4
```

On édite le fichier /etc/systemd/network/enp0s8.network : 

```
[Match]
Name=enp0s8

[Network]
Address=10.1.0.1/24
Gateway=10.1.0.2
```

Pour que notre machine *gateway1* puisse router correctement les paquets, on active l'IP Forwarding : 
```sysctl -w net.ipv4.ip_forward=1``` et on change la valeur du fichier ```/etc/sysctl.conf```

On met à jour les configurations réseaux avec ```$ systemctl restart systemd-networkd```

On fera de la même manière les configurations réseaux de *client2* et *gateway2*
Si toutes les configurations sont correctes, *client1* et *client2* pourront se ping.

## Parefeu Netfilter

### Définition

Netfilter est un framework implémentant un pare-feu au sein du noyau Linux. Il permet l'interception et la manipulation des paquets réseau lors des appels des routines de réception ou d'émission des paquets des interfaces réseau.
Nous utiliserons donc **iptables** pour créer nos pare-feux dans notre réseau local.

### Commandes utiles

Il y a 3 états possibles d'un paquet : 
- la source est la machine : *INPUT*
- la destination est la machine : *OUTPUT*
- la machine doit router le paquet : *FORWARD*

- ```$ iptables -nvL``` permet d'afficher les règles du pare-feu de la machine
- ```$ iptables -F``` permet de supprimer toutes les règles du pare-feu de la machine
- ```$ iptables -P OUTPUT DROP``` permet de changer la politique de OUTPUT et de bloquer tous les paquets par défaut
- ```$ iptables -A OUTPUT -d 10.1.1.1 -j ACCEPT``` permet d'accepter uniquement les paquets dont la destination est 10.1.1.1
- ```$ iptables -A FORWARD -s 10.1.0.2 -d 10.1.0.2 -j DROP``` (utile sur *gateway1*) permet de bloquer les paquets dont la source est 10.1.0.2 et la destination 10.1.0.2. 

### Différence entre stateless firewalls et stateful firewalls

Un parefeu dit *stateless* n'a pas de mémoire et donc il ne peut pas différencier de manière intelligente une réponse à un paquet d'une attaque venant de l'extérieur. C'est pour cela qu'on utilise maintenant les parefeux dits *stateful*. 
Ce qu'on aimerait donc serait d'autoriser les paquets HTTP (port destination 80) à sortir mais bloquer les paquets dont le port 80 est la source **SAUF** si c'est une réponse à un paquet venant de l'extérieur. 

Les règles de base à établir sont donc les suivantes : 
- concernant *client1* et *client2* : 
```
$ iptables -P INPUT DROP
# la politique de base pour INPUT est de bloquer les paquets
$ iptables -P FORWARD DROP
# la politique de base pour FORWARD est de bloquer les paquets
$ iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
# on accepte les paquets uniquement pour les connexions déjà établiées
$ iptables -A INPUT -i lo -j ACCEPT
# on accepte les paquets reçus sur la boucle locale (127.0.0.1)
$ iptables -A INPUT -s 10.1.1.1 -j ACCEPT 
# on accepte les paquets envoyés par la gateway1 car elle appartient au même sous-réseau
```

- concernant *gateway1* :
```
$ iptables -P INPUT DROP
# la politique de base pour INPUT est de bloquer les paquets
$ iptables -A INPUT -s 10.1.1.2 -j ACCEPT
# les paquets venant de client1 sont acceptés car client1 appartient au même sous-réseau
$ iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
# on accepte les paquets uniquement pour les connexions déjà établiées
$ iptables -A INPUT -i lo -j ACCEPT
# on accepte les paquets reçus sur la boucle locale (127.0.0.1)
```
On aimerait également cacher les adresses IP privées du sous réseau 10.1.1.0. Pour cela, on peut établir une règle sur *gateway1* qui va changer l'adresse source de *client1* : 

```
$ iptables -t nat -A POSTROUTING -s 10.1.1.2 -j SNAT --to 10.1.0.1
# l'adresse source sera maintenant 10.1.0.1 au lieu de 10.1.1.2
$ iptables -nvL -t nat
# permet de visualiser les règles de NAT
```
Ainsi, lorsque l'on fait ```tcpdump -n -i enp0s3``` sur *client2* lors de ping de *client1* vers *client2*, on voit des paquets ICMP communiqués entre *gateway1* et *client2* (et non entre *client1* et *client2* avant cette configuration).

## Tunnel GRE

Generic Routing Encapsulation (GRE) est un protocole de mise en tunnel qui permet d'encapsuler n'importe quel paquet de la couche réseau (donc de couche OSI 3) dans sa conception d'origine. Le paquet d'origine est le payload (information utile) du paquet final. Par exemple, les serveurs de tunnel qui chiffrent les données peuvent utiliser GRE à travers Internet pour sécuriser les Réseaux privés virtuels. 

Nous voulons créer un tunnel GRE entre *gateway1* et *gateway2* et activer la route dans ce tunnel. Pour cela, on fait les commandes suivantes : 

- sur *gateway1* : 
```
$ ip tunnel add gre_tunnel mode gre local 10.1.0.1 remote 10.1.0.2
# création du tunnel entre 10.1.0.1 et 10.1.0.2
$ ip link set gre_tunnel up
# activation du tunnel
$ ip route del 10.1.2.0/24 via 10.1.0.2
# suppression de la route par défaut
$ ip route add 10.1.2.0/24 dev gre_tunnel
# création de la route dans le tunnel
```

- sur *gateway2* : 
```
$ ip tunnel add gre_tunnel mode gre local 10.1.0.2 remote 10.1.0.1
# création du tunnel entre 10.1.0.2 et 10.1.0.1
$ ip link set gre_tunnel up
# activation du tunnel
$ ip route del 10.1.1.0/24 via 10.1.0.1
# suppression de la route par défaut
$ ip route add 10.1.1.0/24 dev gre_tunnel
# création de la route dans le tunnel
```

## IPSec

IPSec (Internet Protocol Security) est un ensemble de protocoles utilisant des algorithmes permettant le transport de données sécurisées sur un réseau IP. 
Il est composé de deux sous protocoles : 
- *AH* qui propose de l'authentification et de l'intégrité (par le biais du transport point-à-point et du tunnelage)
- *ESP* qui propose de l'authentification, de l'intégrité et du chiffrement (par le biais de la couche transport et du tunnelage)

### Configuration 

Pour configurer correctement IPSec sur les machines, il faut établir des règles pour la SAD et la DPD. 
- La SPD (Security Policy Database) permet de savoir ce que l’on doit faire (utiliser un Security Association ou pas) avec un paquet donné. Chacune des entrées de la SPD définit un sous-ensemble du trafic IP et des points vers une SA pour ce trafic.
- La SAD (Security Association Database) fournit toutes les informations pour émettre vers X, à savoir le SPI, la clé, les algorithmes utilisés, le numéro de séquence courant etc… De même, à la réception d’un paquet, le SPI du paquet est utilisé pour trouver l’entrée correspondante dans la base de données des SAs. Le récepteur connaitra donc les paramètres pour décoder le paquet.

Pour cela, on va créer un fichier de configurations pour chaque gateway *ipsec.conf*

#### Configuration de *gateway1*

```
# gateway1 :
flush ;
spdflush ;
spdadd 10.1.0.1 10.1.0.2 any -P out ipsec esp/transport//require ;
spdadd 10.1.0.2 10.1.0.1 any -P in ipsec esp/transport//require ;
add 10.1.0.1 10.1.0.2 esp 0x305 -m transport -E aes-cbc ”2234567890123456” -A
hmac-sha1 ”22345678901234567890” ;
add 10.1.0.2 10.1.0.1 esp 0x306 -m transport -E aes-cbc ”1234567890123456” -A
hmac-sha1 ”12345678901234567890” ;
```

#### Configuration de *gateway2*

```
# gateway2 :
flush ;
spdflush ;
spdadd 10.1.0.1 10.1.0.2 any -P in ipsec esp/transport//require ;
spdadd 10.1.0.2 10.1.0.1 any -P out ipsec esp/transport//require ;
add 10.1.0.1 10.1.0.2 esp 0x305 -m transport -E aes-cbc ”2234567890123456” -A
hmac-sha1 ”22345678901234567890” ;
add 10.1.0.2 10.1.0.1 esp 0x306 -m transport -E aes-cbc ”1234567890123456” -A
hmac-sha1 ”12345678901234567890” ;
```
#### Application de la configuration 

Pour appliquer les configurations de IPSec, on fait sur les deux gateways :

```
setkey -f ipsec.conf
setkey -D
setkey -DP
```

Pour activer ces règles dès le démarrage de la machine, il faut faire : 
```
cp ipsec.conf /etc/ipsec-tools.d/ipsec.conf
```

On peut également utiliser le paquet *racoon* qui fournit un démon qui gère toutes les phases d'échanges de clé IKE.
