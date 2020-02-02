# Proxy

Ce dépôt va expliquer comment réaliser un proxy HTTP et le configurer. 
Pour cela, toutes les requêtes du client va passer par le proxy. Ce sera le proxy qui réalisera les requêtes HTTP. Pour créer ce proxy, nous l'avons implémenté dans *proxy.py* et se déclenche avec la commande suivante ```python proxy.py```. 
Pour que le navigateur puisse savoir sur quel port et adresse envoyer les requêtes, il faut configurer celui-ci. 

Sachant que notre proxy est sur *lo* (127.0.0.1) sur le port 8080, on configure le navigateur dans les paramètres du navigateur :

<img src="/doc/config_firefox.PNG">
