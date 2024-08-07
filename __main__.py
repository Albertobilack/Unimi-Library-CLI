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
#DA CONTROLLARE COSA SUCCEDE SE POSTI PRENOTABILI PER UN ORARIO SONO 0, SE VENGONO MOSTRATI COMUNQUE E QUINDI VANNO NOTIFICATI COME VUOTI O VENGONO COMPLMETAMENTE
#ESCLUSI DAL JSON
#potrebbe essere utilizzata per mostrare le prenotazoini attive
def freespot_biblio(args): 
    a = Easystaff()
    #a.login(args.u, args.p) #login non necessario

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

# da fare bookbiblio senza login, solo con email e cf
# posso collegare bookbiblio con freespoto o getbiblio e controllare se orari sono prenotabili prima di tentare
#la prenotazione
def book_biblio(args):

    a = Easystaff()
    #a.login(args.u, args.p)
    a.get_book(args.day, args.start, args.end, args.floor)
    # alternativa a.get_book(datetime.strptime(args.day, "%Y-%m-%d"), datetime.strptime(args.start, "%H:%M"), datetime.strptime(args.end, "%H:%M"), args.floor)

    print("ok")
    # da definire piano, per ora preimpostato su piano terra
    # da sistemare input per orario e giorno



if __name__ == "__main__":

    print(" _    _   _   _   _____   __  __   _____")
    print("| |  | | | \\ | | |_   _| |  \\/  | |_   _|")
    print("| |  | | |  \\| |   | |   | \\  / |   | |")
    print("| |  | | | . ` |   | |   | |\\/| |   | |")
    print("| |__| | | |\\  |  _| |_  | |  | |  _| |_")
    print(" \\____/  |_| \\_| |_____| |_|  |_| |_____|\n")


    parser = argparse.ArgumentParser(
        prog = "CLI prenotazione biblioteca",
        description = "script per gestione posti della BICF e reservation automatica dei posti"
    )

    #da sistemare metavar
    parser.add_argument("-u", "--username", dest="u", metavar=None, help="email di istituto", required=False) #da aggiungere default
    parser.add_argument("-p", "--password", dest="p", metavar=None, help="password di istituto", required=False)

    sub = parser.add_subparsers(required=True)

    #elenca posti biblioteca
    #todo : mostrare tutti i giorni liberi per entrambi i piani 
    #todo minore : mostrare solo determinate fasce orarie in base a quante ore prenotare?
    biblio_list = sub.add_parser("list", help="lista degli orari liberi di tutti i posti disponibili per entrambi i piani")
    #biblio_l.add_argument("-piano", help="piano da visualizzare", required=True)
    biblio_list.set_defaults(func=list_biblio)

# idea:
#nota : giorno da prenotare selezionato in base alla posizione dell'array, quindi list deve
#listarli con relative posizioni+1
#farei stessa cosa anche per  orario

    biblio_book = sub.add_parser("book", help="prenotazione della fascia oraria specificata nel giorno specificato")
    biblio_book.add_argument("-day", help="giorno da prenotare nel formato YYYY-MM-DD", required=True)
    biblio_book.add_argument("-floor", help="piano da prenotare: ground | first", required=True, choices=["ground", "first"])
    biblio_book.add_argument("-start", help="ora inizio prenotazione, formato H:M", required=True) # provare ad aggiungere type=datetime.strftime("%Y-%m-%d")
    biblio_book.add_argument("-end", help="ora fine prenotazione, formato H:M", required=True)
    biblio_book.set_defaults(func=book_biblio)

    biblio_freespot = sub.add_parser("freespot", help="lista delle fasce orarie prenotaibli dall'utente in un determinato timeframe (default = 1 ora), con precisazione se già prenotate")
    #biblio_freespot.add_argument("-day", help="giorno da visualizzare", required=True)
    #biblio_freespot.add_argument("-piano", help="piano da visualizzare", required=True)
    biblio_freespot.set_defaults(func=freespot_biblio)


    args = parser.parse_args()
    args.func(args)