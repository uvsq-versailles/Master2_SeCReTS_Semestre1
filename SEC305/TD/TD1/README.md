# ARP-spoofing

Il s'agit ici d'une démonstration de l'ARP Spoofing. Cela consiste à ce qu'un attaquant usurpe l'identité d'un utilisateur. Cela permettra d'écouter le réseau. 
Cette démonstration a été réalisée avec 3 machines virtuelles xubuntu. Ces 3 machines sont dans un même réseau interne (LAN).

## Préparation : attribution des adresses IP

Pour changer l'adresse IP, nous allons créer/modifier le fichier correspondant à l'interface correspondante au réseau à attaquer.

Pour cela, on fait la commande suivante : 

```
$ nano /etc/systemd/network/enp0s3.network

[Match]
Name=enp0s3

[Network]
Address=10.0.0.1/24

```
Pour sauvegarder les changements sur l'interface réseau : ```$ systemctl restart systemd-networkd```

Nous attribuerons les adresses suivantes : 
- machine 1 : 10.0.0.1/24 (Alice)
- machine 2 : 10.0.0.2/24 (Bob)
- machine 3 : 10.0.0.3/24 (Charlie)

## Scanning

Charlie doit connaître son adresse MAC. Pour cela, il utilise ```$ ifconfig -a``` et détermine l'adresse MAC de l'interface réseau associée.
Charlie va scanner le réseau local afin de connaître notamment les adresses IP et MAC de Alice et Bob (qu'il ne connaît pas encore). Pour cela, il utilisera ```$ nmap 10.0.0.0/24```. 

Charlie connaît donc les informations suivantes : 
- **machine 1** : 10.0.0.1/24 08:00:27:5b:5b:32
- **machine 2** : 10.0.0.2/24 08:00:27:6c:e3:94
- **machine 3** : 10.0.0.3/24 08:00:27:00:e7:9d

## Gain Access

### Step 1 : Interception de paquets

Nous allons utiliser l'outil **scapy** afin d'envoyer une requête ARP gratuite à Alice. Au lieu de donner sa véritable IP associé à sa véritable adresse MAC, Charlie va donc envoyer à Alice l'adresse IP de Bob associé à l'adresse MAC de Charlie. Ainsi, Alice va automatiquement changer sa table ARP. Après cela, lorsque Alice voudra envoyer des paquets à Bob, Charlie les interceptera. (Dans cette étape, Charlie ne renvoie pas encore le paquet intercepté à Bob). 

On va donc créer un paquet ARP dont les champs sont les suivants : 
- **adresse MAC de la source** : MAC de Charlie (08:00:27:00:e7:9d) -> hwsrc
- **adresse IP de la source** : IP de Bob (10.0.0.2) -> psrc
- **adresse MAC de la destination** : MAC de Alice (08:00:27:5b:5b:32) -> dst

```
$ scapy
>>> p=Ether()/ARP()
>>> p.hwsrc = '08:00:27:00:e7:9d'
>>> p.psrc = '10.0.0.2'
>>> p.dst = '08:00:27:5b:5b:32'
>>> sendp(p, iface='enp0s3')
```
### Step 2 : Man-in-the-Middle

Afin de réaliser une écoute entre Alice et Bob, il ne faut pas seulement intercepter le trafic mais aussi le répéter. Pour cela, 
Charlie doit configurer sa machine comme un routeur : c'est l'**IP Forwarding**. De plus, il faut envoyer un GARP (Gratuitous ARP) à Alice pour se faire passer pour Bob et aussi envoyer un GARP à Bob pour se faire passer pour Alice. Sachant que les machines de Alice et de Bob vont également envoyer des paquets ARP pour s'identifier régulièrement, il faut que Charlie envoie de manière répétée ses GARP. 

J'ai donc écrit le script spoofing.py qui s'exécute avec ```python spoofing.py``` et qui réalise cette attaque Man-in-the-Middle. Ainsi, on pourra voir le trafic qui transite entre Alice et Bob.


