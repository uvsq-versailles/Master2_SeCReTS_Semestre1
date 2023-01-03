# Corrections des questions (sans ordre)

- **Examen 2021-2022 :** QCM
- **Examen 2016-2017**
- **Examen 2010-2011 :** (2 parties, 6 pages)

## Couche de niveau 2

### Rappelez le principe du protocole ARP. Comment feriez-vous pour mettre en évidence les attaques de ce type contre votre machine ?

> ARP est un protocole sans état. Un attaquant peut envoyer des fausse réponse ARP sur une station pour forcer la mise à jour des caches des stations. -> le paquet ARP : @IP_victime, @MAC_pirate
>
> 4 solutions :
>
> - Table arp statique en figeant l'association IP/MAC
> - Gratuitous ARP : N'autorise les réponse ARP uniquement si une requete ARP a été enregistrée précédemment. Seules les réponses en rapport avec la requetes seront autorisées à transiter.
> - IDS : Analyse d'un grand nombre de paquets ARP-reply envoyé lève une alerte aux équipes de sécurité.
> - DAI : Pour chaque réponse ARP envoyé depuis un port qui n'est pas de confiance, comparer les données qu'elle contient à une base de données de confiance pré-enregistrée dans le réseau et dropper les paquets arp-reply contenant de fausses informations.

---

> **ARP spoofing :** Usurper l'identité de passerelle par défaut avec adresse mac.
>
> **Identification :** `iproute` pour savoir passerelle par défaut.Dans le cas normal on envoit les données on passe par la passerelle en envoyant l'@ mac src et l'@ mac dest du passerelle .
>
> Mais si un attaquant veut faire ce type d'attaque, il dit que c 'est lui la paserelle. Qd on a lancé ARP request ou il donne desarp réponses gratuites (sans lui demander il dit c moi le paserelle c moi ..) et il sera lui l'intermidiaire comme ça.
>
> Soit avec `tcdump` ou `ids` (intrusion detection system)/reponses gratuites sans demande
>
> **Prémunir :** `ARP static` on fait pas des demandes arp (on fait pas arp request) ; on entre seulement aux sites HTTPS ; utiliser VPN tunnel chiffré

## Couche de niveau 3 / IP

### **Format des datagrammes IP :** Quelle est la taille maximale (en octets) de a PCI *("Protocol Control Information" dans le vocabulaire OSI)* contenue dans un datagramme IP ?

> Taille PCI : dans 99% des cas la taille est de 20 octets. Si le champs options est utilisé la taille maximum est alors de 60 octets.

### **Découpage CIDR**

---

### **TTL** *(Time to Live)*

> Durée de vie de paquet nbr de saut combien de routeurs a traversé.

**Est-ce la même valeur pour tous les paquets ?**
> Non car les routeurs  distribuent les paquets de façons optimales

### **Champ IHL**

> Le champ IHL dans l'entete datagramme ip (ip header) indique la taille de l'entete en nombre de mot de 32 bits .
>
> Champ de taile 4 bits maximal donc 2 puiss 4 -1  =15 mot de 32 bits.
>
> 15*4=60 octets. \
> min 20 et max 60

**Quelle est la taille de user data autre ex ?**

> (2 puiss 16 -1 )-20 ip header.. en octets \
> 16 car champ sur 2 octet -1  \
> 20: taille minimal de l entete ip

---

### Paquet ICMP

> dans la réponse echo replay .. il y a des données aléatoires qui sont rajoutées pour atteindre une longueur minimalen.
>
> on remarque que dans ces données on distingue adm et pass on peut supposer qu il a copié ces données à partir d'un buffer.

### UDP / TCP

> - arp spoofing faut n etre sur le meme réseau
> - ip spoofing n'importe quelle machine.
> - UDP car on établie pas la connexion.
> - car en tcp ..on envoie syn après le syn ack sera pas envoyé à moi car c mpas moi le bon source
> - en syn ack normalement on reçoit un numéro de séquencement
> - mais psq je vais pas le recevoir psq je suis pas la bonne destination
> - donc je ne peux pas répondre par ack car je n'ai pas le numéro de séquencement pour répondre et établir la connexion.
> - les conditions particulières
