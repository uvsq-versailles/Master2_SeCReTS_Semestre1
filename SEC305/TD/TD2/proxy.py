import os,sys,thread,socket

### Constantes ###

# Nombre de connexions en attente peuvent tenir en meme temps
BACKLOG = 50

# Nombre d'octets au maximum qu'on peut recevoir en une seule fois
MAX_DATA_RECV = 999999

# Variables de debuggage a True pour voir les messages en cas de probleme
DEBUG = True

# Lien URL qui doivent etre bloque
BLOCKED = ['sebastienguillon.com']

# Numero du port pour ce proxy 
PORT = 8080

# Adresse IP du proxy 
HOST = '127.0.0.1'

### Fonction principale ###
def main():
    
    print "Proxy Server Running on ",HOST,":",PORT

    try:
        # creation du socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # association du socket avec le port 8080 et l'adresse IP 127.0.0.1
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))

        # socket en ecoute
        s.listen(BACKLOG)
    
    except socket.error, (value, message):
        if s:
            s.close()
        print "Could not open socket:", message
        sys.exit(1)

    # association du socket avec la connexion du client
    while 1:
        try:
            conn, client_addr = s.accept()
            
            # creation du thread pour manipuler la requete du client
            thread.start_new_thread(proxy_thread, (conn, client_addr))

        except KeyboardInterrupt:
            s.close()
            exit()  
     
    s.close()

# Fonction pour gerer les erreurs lors des requetes entre le client et le serveur
def printout(type,request,address):
    if "Block" in type or "Blacklist" in type:
        colornum = 91
    elif "Request" in type:
        colornum = 92
    elif "Reset" in type:
        colornum = 93

    print "\033[",colornum,"m",address[0],"\t",type,"\t",request,"\033[0m"

# Fonction qui permet de manipuler la requete du client
def proxy_thread(conn, client_addr):

    # recuperation de la requete entiere du client
    request = conn.recv(MAX_DATA_RECV)
    
    # recuperation de la premiere ligne de la requete 
    first_line = request.split('\n')[0]

    # recuperation de l'URL de la requete
    url = ''
    parts = first_line.split(' ')
    for i in range(0,len(parts)):
        if parts[i][0:4] == 'http':
            url = parts[i]

    # filtrage des sites web blackliste
    for i in range(0,len(BLOCKED)):
        if BLOCKED[i] in url:
            printout("Blacklisted",first_line,client_addr)
            conn.close()
            sys.exit(1)

    printout("Request",first_line,client_addr)
    
    # recherche du serveur et de son port
    http_pos = url.find("://")          # find pos of ://
    if (http_pos==-1):
        temp = url
    else:
        temp = url[(http_pos+3):]       # get the rest of url
    
    port_pos = temp.find(":")           # find the port pos (if any)

    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos==-1 or webserver_pos < port_pos):
        port = 80
        webserver = temp[:webserver_pos]
    else:    
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]

    try:
        # creation du socket qui va se connecter au serveur web
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        s.connect((webserver, port))
        s.send(request) 
        
        while 1:
            # reception des donnees envoyees par le serveur
            data = s.recv(MAX_DATA_RECV)
            
            if (len(data) > 0):
                conn.send(data)
            else:
                break
        s.close()
        conn.close()
    except socket.error, (value, message):
        if s:
            s.close()
        if conn:
            conn.close()
        printout("Peer Reset",first_line,client_addr)
        sys.exit(1)

# Appel a la fonction principale
if __name__ == '__main__':
    main()


