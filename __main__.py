#tutte le exception vanno sistemate

#credit to https://github.com/Mroik for some of logic behind this script

import argparse
from easystaff import Easystaff
from datetime import datetime

#NON NECESSITA DI LOGIN
def list_biblio(args): 
    a = Easystaff()
    #a.login(args.u, args.p)

    biblioTerra, biblioPrimo = a.get_biblio()
    biblioTerra = (biblioTerra["schedule"])
    print("PIANO TERRA")
    for i in biblioTerra:
        print("giorno:", i)
        contatore = 1
        for j in biblioTerra[i]:
            print(contatore, ":", j)
            contatore += 1

    if biblioPrimo["prima_disp"] == None:
        print("0 POSTI PRENOTABILI AL PRIMO PIANO")
    else:
        biblioPrimo = (biblioPrimo["schedule"])
        print("PRIMO PIANO")
        for i in biblioPrimo:
            print("giorno:", i)
            contatore = 1
            for j in biblioPrimo[i]:
                print(contatore, ":", j)
                contatore += 1


# da cambiare presentazione delle informazioni : se slot["reserved"] = false scrivo a terminale prenotabile
# se slot["reserved"] = true scrivo a terminale non prenotabile
def freespot_biblio(args): 
    a = Easystaff()
    a.login(args.u, args.p)

    biblioTerra, biblioPrimo = a.get_freespot()
    biblioTerra = (biblioTerra["schedule"])
    data = list(biblioTerra.keys())[0]
    biblioTerra = (biblioTerra[data])
    print("PIANO TERRA, giorno:", data)
    for orario, slot in biblioTerra.items():
        if slot["disponibili"] > 0:
            print(orario, "| presente prenotazione:", slot["reserved"])

    biblioPrimo = (biblioPrimo["schedule"])
    data = list(biblioPrimo.keys())[0]
    biblioPrimo = (biblioPrimo[data])
    print("PRIMO PIANO, giorno:", data)
    for orario, slot in biblioPrimo.items():
        if slot["disponibili"] > 0:
            print(orario, "| presente prenotazione:", slot["reserved"])

def book_biblio(args):
    TS_DAY = datetime.strptime(args.day, "%Y-%m-%d")
    TS_ORAINZIO = datetime.strptime(args.inizo, "%Y-%m-%d")
    TS_ORAFINE = datetime.strptime(args.fine, "%Y-%m-%d")
    TS_INIZIO = TS_DAY+TS_ORAINZIO
    TS_FINE = TS_DAY+TS_ORAFINE

    a = Easystaff()
    a.login(args.u, args.p)
    a.book_bibio(TS_INIZIO, TS_FINE)
    print("ok")
    #da definire piano, per ora preimpostato su piano terra
    #da sistemare input per orario e giorno



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    )

    parser.add_argument("-u", help="email", required=True) #da aggiungere default
    parser.add_argument("-p", help="password", required=True)

    sub = parser.add_subparsers(required=True)

    #elenca posti biblioteca
    #todo : mostrare tutti i giorni liberi per entrambi i piani 
    #todo minore : mostrare solo determinate fasce orarie in base a quante ore prenotare?
    biblio_l = sub.add_parser("list")
    #biblio_l.add_argument("-piano", help="piano da visualizzare", required=True)
    biblio_l.set_defaults(func=list_biblio)

    biblio_l = sub.add_parser("book")
    #biblio_l.add_argument("-day", help="giorno da prenotare", required=True)
    #biblio_l.add_argument("-piano", help="piano da prenotare", required=True)
    biblio_l.set_defaults(func=book_biblio)

    biblio_l = sub.add_parser("freespot")
    #biblio_l.add_argument("-day", help="giorno da visualizzare", required=True)
    #biblio_l.add_argument("-piano", help="piano da visualizzare", required=True)
    biblio_l.set_defaults(func=freespot_biblio)




    #nota : giorno da prenotare selezionato in base alla posizione dell'array, quindi list deve
    #listarli con relative posizioni+1
    #farei stessa cosa anche per orario
    #book_l = sub.add_parser("book")
    #book_l.add_argument("-d", help="giorno da prenotare", required=True)
    #book_l.add_argument("-p", help="piano da prenotare (T / P)", required=True)
    #book_l.add_argument("-h", help="orario")



    args = parser.parse_args()
    args.func(args)




    #list_l = sub.add_parser("list")
    #list_l.set_defaults(func=list_lessons)

    #book_l = sub.add_parser("book")
    #book_l.add_argument("-cf", help="fiscal code", required=True)
    #book_l.add_argument("-e", help="the id of the lesson")
    #book_l.add_argument("-a", help="book everything available", action="store_true")
    #book_l.set_defaults(func=book_lesson)