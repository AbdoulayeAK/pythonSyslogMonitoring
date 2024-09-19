import json
from flask import Flask

app = Flask(__name__)

@app.route("/")
def clients():
    fichierReject = open("data/fichierReject.json", "r")
    dictMain = ""
    dictMainTempsMax = ""

    for ligne in fichierReject:
        dictMain = ligne


    dictMain = dictMain.replace("'", '"')
    result = json.loads(dictMain)

    print(f"dictMain : {dictMain}\nType : {type(dictMain)}\n")
    print(f"Result : {result}\nType : {type(result)}")
    if result["Clients"] == []:
        return "Aucun client rejeté !"
    return result

@app.route("/tempsMax")
def clientsTempsMax():
    fichierRejectTempsMax = open("data/fichierRejectTempsMax.json", "r")
    dictMainTempsMax = ""

    for ligne in fichierRejectTempsMax:
        dictMainTempsMax = ligne

    dictMainTempsMax = dictMainTempsMax.replace("'", '"')
    resultTempsMax = json.loads(dictMainTempsMax)

    print(f"dictMain : {dictMainTempsMax}\nType : {type(dictMainTempsMax)}\n")
    print(f"Result : {resultTempsMax}\nType : {type(resultTempsMax)}")
    if resultTempsMax["Clients"] == []:
        return "Aucun client rejeté !"
    return resultTempsMax


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
