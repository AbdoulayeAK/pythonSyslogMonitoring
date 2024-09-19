import json
from datetime import datetime
from datetime import timedelta
import socketserver
print("Lancement du programme ...\n\n\n")

#Tableaux contenant les adresses MAC des clients rejetés
tabReject = []
tabRejectCat1 = []

#Dictionnaires contenant les informations sur les clients rejetés (LT, MAC, Port...)
dictClients = {}
dictClientsTempsMax = {}

tabClients = []
tabClientsTempsMax = []

dictHeure = {}

tempsRejetMax = timedelta(minutes=20)
tempsRejetExclusion = timedelta(minutes=45)
fichierReject = open("data/fichierReject.json", "w+")
fichierRejectTempsMax = open("data/fichierRejectTempsMax.json", "w+")

class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        elements = str(self.request[0]).split("|")[-1]
        elementsSplit = str(elements).split("\\t")
        #print(f"request : {self.request}")
        #print(f"elements : {elements}")
        #print(f"elementsSplit : {elementsSplit}\n")

        dictFull = {}
        dictReject = {}
        dictID = {}
        tabRejectTempsMax = []

        if "Filaire" in str(self.request[0]):
            print("-------------------------------Début request-------------------------------\n")
            for i in range(len(elementsSplit)):
                # Séparation de chaque élément récupéré dans le dictionnaire "dictFull"
                dictFull[elementsSplit[i].split("=")[0]] = elementsSplit[i].split("=")[1]
            print(f"dictFull : {dictFull}\n")
            if dictFull != {}:
                if dictFull['statut_connexion'] != "ACCEPT" and dictFull["mac"] not in tabReject:
                    tabReject.append(dictFull["mac"])

                    # Ajout des infos du clients dans le dictionnaire "dictReject"
                    dictReject["MAC"] = dictFull["mac"]
                    dictReject["Port"] = dictFull["port"]
                    if dictFull["ip_nas"][8] == ".":
                        dictReject["LT"] = "SPARE"
                        dictReject["nSwitch"] = 1
                    else:
                        dictReject["LT"] = dictFull["ip_nas"][8:10]
                        dictReject["nSwitch"] = int(dictFull["ip_nas"][-1])
                    tabDate = []
                    tabDate.append(dictFull["heure"][0:10])  # Date
                    tabDate.append(dictFull["heure"][11:-3]) # Heure
                    dictReject["Heure"] = tabDate

                    # Ajout d'une clé (adresse MAC) qui contient le dictionnaire du client
                    dictID[dictFull["mac"]] = dictReject

                    # Ajout de chaque client au tableau "tabClients"
                    tabClients.append(dictID)

                    # Ajout d'une clé MAC relié à l'heure et la date du premier rejet au dictionnaire "dictHeure"
                    dictHeure[dictFull["mac"]] = tabDate

                    # Ajout du tableau "tabClients" au dictionnaire "dictPrincipal" (afin de passer les données sous forme JSON)
                    dictClients["Clients"] = tabClients


                if dictFull['statut_connexion'] == "ACCEPT" and dictFull["mac"] in tabReject:
                    print(tabRejectCat1)
                    # Effacement de l'adresse MAC dans le tableau "tabReject" si l'appareil est accepté
                    tabReject.remove(dictFull["mac"])
                    # On effectue la même action sur le tableau "tabRejectCat1"
                    if dictFull["mac"] in tabRejectCat1:
                        tabRejectCat1.remove(dictFull["mac"])

                    # Effacement de l'adresse MAC dans le tableau "tabClients" situé dans le dictionnaire "dictClients" si l'appareil est accepté
                    for elt in dictClients["Clients"]:
                        if dictFull["mac"] in elt:
                            dictClients["Clients"].remove(elt)
                    # On effectue la même action sur le tableau "tabClientsTempsMax" situé dans le dictionnaire "dictClientsTempsMax"
                    for elt in dictClientsTempsMax["Clients"]:
                        if dictFull["mac"] in elt:
                            dictClientsTempsMax["Clients"].remove(elt)

                    print(f"Avertissement : L'appareil avec l'adresse MAC : \"{dictFull["mac"]}\" a maintenant accès au réseau !")

            dateActuelle = str(datetime.now())[0:10]
            heureActuelle = str(datetime.now())[11:-7]
            #Partie de vérification du temps de rejet
            if dictHeure != {}:
                dictHeureIteration = dictHeure.copy()
                print(f"Heure actuelle : {heureActuelle}")
                print(f"dictHeure : {dictHeure}")

                for mac in dictHeureIteration:
                    # Si le client est rejeté pendant plus de "tempsRejetMax" minutes consécutives, il sera placé dans le tableau "tabRejectCat1"
                    if datetime.strptime(heureActuelle, "%H:%M:%S") - datetime.strptime(dictHeure[mac][1], "%H:%M:%S") > tempsRejetMax or dateActuelle != dictHeure[mac][0]:
                        print(f"L'appareil avec l'adresse MAC {mac} est rejeté depuis plus de {tempsRejetMax} minutes.\nPassage dans la catégorie +{str(tempsRejetMax)[2:4]} minutes.\n")
                        tabRejectCat1.append(mac)
                        dictHeure.pop(mac)
                        tabClientsIteration = tabClients.copy()
                        for infosClient in tabClientsIteration:
                            print(f"Infos client dans tabClients : {infosClient}")
                            if mac in infosClient:
                                tabClientsTempsMax.append(infosClient)
                                tabClients.remove(infosClient)
                                print(f"L'appareil avec l'adresse MAC {mac} a été retiré du tableau des clients et ajouté au dictionnaire \"dictClientsTempsMax\"!\n")
                dictClientsTempsMax["Clients"] = tabClientsTempsMax

            # Dans cette partie, on retire les clients qui sont rejetés depuis plus de "tempsRejetExclusion"
            for infosClient in dictClientsTempsMax["Clients"]:
                for key in infosClient.keys():
                    if datetime.strptime(heureActuelle, "%H:%M:%S") - datetime.strptime(infosClient[key]["Heure"][1], "%H:%M:%S") > tempsRejetExclusion:
                        for client in dictClientsTempsMax["Clients"]:
                            if infosClient[key]["MAC"] in client:
                                dictClientsTempsMax["Clients"].remove(client)
                                tabReject.remove(infosClient[key]["MAC"])
                                tabRejectCat1.remove(infosClient[key]["MAC"])
                        print(f"{tempsRejetExclusion} minutes dépassé, exlcusion de l'appareil avec l'adresse MAC \"{infosClient[key]["MAC"]}\"")
            print(f"\nVoici les adresses MAC activement rejetées : {tabReject}")
            print(f"Voici les adresses MAC activement rejetées en catégorie +{tempsRejetMax} minutes : {tabRejectCat1}\n")

            print(f"Dictionnaire de l'API : {dictClients}\n")
            print(f"Dictionnaire de l'API tempsMax : {dictClientsTempsMax}\n")

            print(f"tabClients après remove: {tabClients}\n")
            print(f"tabClientsTempsMax après append: {tabClientsTempsMax}\n")
            print("--------------------------------Fin request--------------------------------\n\n\n\n")
            fichierReject = open("data/fichierReject.json", "w+")
            fichierReject.write(str(dictClients))

            fichierRejectTempsMax = open("data/fichierRejectTempsMax.json", "w+")
            fichierRejectTempsMax.write(str(dictClientsTempsMax))



if __name__ == "__main__":
    #Renseignement de l'adresse IP du serveur Syslog et ouverture du port de la machine
    with socketserver.UDPServer(("Serveur syslog (int)", "Port du serveur syslog (int)"), UDPHandler) as server:
        server.serve_forever()