#credit to https://github.com/Mroik for some of logic behind this script

import argparse
from easystaff import Easystaff

def list_biblio(args): 
    a = Easystaff()
    groundLibrary, firstLibrary = a.get_list()

    if firstLibrary["prima_disp"] == None:
        print("0 AVAIBLE SPOT AT GROUND FLOOR")
    else:    
        groundLibrary = (groundLibrary["schedule"])
        print("GROUND FLOOR")
        for i in groundLibrary:
            print("date:", i)
            contatore = 1
            for j in groundLibrary[i]:
                print(contatore, ":", j)
                contatore += 1

    if firstLibrary["prima_disp"] == None:
        print("0 AVAIBLE SPOT AT FIRST FLOOR")
    else:
        firstLibrary = (firstLibrary["schedule"])
        print("FIRST FLOOR")
        for i in firstLibrary:
            print("date:", i)
            contatore = 1
            for j in firstLibrary[i]:
                print(contatore, ":", j)
                contatore += 1


# da cambiare presentazione delle informazioni : se slot["reserved"] = false scrivo a terminale prenotabile
# se slot["reserved"] = true scrivo a terminale non prenotabile
#DA CONTROLLARE COSA SUCCEDE SE POSTI PRENOTABILI PER UN ORARIO SONO 0, SE VENGONO MOSTRATI COMUNQUE E QUINDI VANNO NOTIFICATI COME VUOTI O VENGONO COMPLMETAMENTE
#ESCLUSI DAL JSON
#potrebbe essere utilizzata per mostrare le prenotazoini attive
def freespot_biblio(args): 
    a = Easystaff()
    groundLibrary, firstLibrary = a.get_freespot(args.tf)
    groundLibrary = (groundLibrary["schedule"])
    data = list(groundLibrary.keys())[0]
    groundLibrary = (groundLibrary[data])
    print("GROUND FLOOR, date:", data)
    for orario, slot in groundLibrary.items():
        if slot["disponibili"] > 0:
            print(orario, "| active reservation:", slot["reserved"])

    firstLibrary = (firstLibrary["schedule"])
    data = list(firstLibrary.keys())[0]
    firstLibrary = (firstLibrary[data])
    print("FIRST FLOOR, date:", data)
    for orario, slot in firstLibrary.items():
        if slot["disponibili"] > 0:
            print(orario, "| active reservation:", slot["reserved"])

# da fare bookbiblio senza login, solo con email e cf
# posso collegare bookbiblio con freespoto o getbiblio e controllare se orari sono prenotabili prima di tentare
#la prenotazione
def book_biblio(args):

    a = Easystaff()
    a.login()
    a.get_book(args.day, args.start, args.end, args.floor)
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
        description = "script per gestione posti della BICF e reservation automatica dei posti. Use '<command> -h' for details of an argument"
    )

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
    #biblio_book.add_argument("-u", "--username", dest="u", metavar=None, help="email di istituto", required=True) #da aggiungere default, da sistemare metavar
    #biblio_book.add_argument("-p", "--password", dest="p", metavar=None, help="password di istituto", required=True)
    biblio_book.set_defaults(func=book_biblio)

    biblio_freespot = sub.add_parser("freespot", help="lista delle fasce orarie prenotaibli in un determinato timeframe, viene precisato se già prenotate o prenotabili se indicato il CF dell'utente")
    biblio_freespot.add_argument("-tf", help="ampiezza della fascia oraria da visualizzare in ore; default = 1 ", required=False, type=int, default=1)
    #biblio_freespot.add_argument("-day", help="giorno da visualizzare", required=True)
    #biblio_freespot.add_argument("-piano", help="piano da visualizzare", required=True)
    biblio_freespot.set_defaults(func=freespot_biblio)


    args = parser.parse_args()
    args.func(args)