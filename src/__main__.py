import argparse
from easystaff import Easystaff
from time import sleep
from datetime import datetime, timedelta, date
import pytz
import config

def list_library(args): 
    a = Easystaff()
    groundLibrary, firstLibrary = a.get_list()

    if groundLibrary["prima_disp"] == None:
        print("0 AVAILABLE SPOT AT GROUND FLOOR")
    else:    
        groundLibrary = (groundLibrary["schedule"])
        print("GROUND FLOOR")
        for i in groundLibrary:
            print("date:", i)
            alreadyListed = []
            for j in groundLibrary[i]:
                if j not in alreadyListed:
                    alreadyListed.append(j)
                    print("-", j)

    if firstLibrary["prima_disp"] == None:
        print("\n0 AVAILABLE SPOT AT FIRST FLOOR")
    else:
        firstLibrary = (firstLibrary["schedule"])
        print("\nFIRST FLOOR")
        for i in firstLibrary:
            print("date:", i)
            iteration = 1
            alreadyListed = []
            for j in firstLibrary[i]:
                if j not in alreadyListed:
                    alreadyListed.append(j)
                    print(iteration,  ":" + j)
                    iteration += 1

# DO NOT USE DATE INSTEAD OF DAY
def freespot_library(args): 
    a = Easystaff()
    groundLibrary, firstLibrary = a.get_freespot(args.tf)

    if groundLibrary["schedule"] == {}:
        print("0 AVAILABLE SPOT AT FIRST FLOOR")
    else: 
        print("GROUND FLOOR")
        for day in groundLibrary["schedule"]:
            print("date:", day)
            day = groundLibrary["schedule"][day]
            #if day == {}:
            #    print("0 POSTI DISPONIBILI")
            for timeslot, reservation in day.items():
                if reservation["disponibili"] > 0:
                    print("-", timeslot, "| active reservation:", reservation["reserved"])

    day = str(date.today())
    if firstLibrary["schedule"] == [] or firstLibrary["schedule"][day] == {}:
        print("\n0 AVAILABLE SPOT AT FIRST FLOOR")
    else:
        firstLibrary = (firstLibrary["schedule"][day])
        print("\nFIRST FLOOR\ndate:", day)
        # if firstLibrary == {}:
        #     print("0 POSTI DISPONIBILI")
        for timeslot, reservation in firstLibrary.items():
            if reservation["disponibili"] > 0:
                print(timeslot, "| active reservation:", reservation["reserved"])


def wait_start():
    startTime = "00:05"
    startTime = datetime.strptime(startTime, "%H:%M").time()
    limitTime = "00:00"
    limitTime = datetime.strptime(limitTime, "%H:%M").time()
    cet = pytz.timezone("CET")

    while limitTime < datetime.now(cet).time():
        sleep(120)

    while startTime > datetime.now(cet).time():
        sleep(15)


def book_library(args):

    if args.subArgument == "quick":
        if args.now :                           #SICURO DI VOLER TENERE LA POSSIBILITÀ DI ESEGUIRE LO SCRIPT QUICK IN 
            today = datetime.today()            #IN 2 GIORNI DIVERSI?
            args.day = today.strftime("%Y-%m-%d")
        else:
            today = datetime.today() + timedelta(days=1)
            args.day = today.strftime("%Y-%m-%d")        
        args.start = config.START
        args.end = config.END
        args.floor = config.FLOOR

    if not args.now :
        wait_start()

    a = Easystaff()
    a.login()
    reservationStatus = a.get_book(args.day, args.start, args.end, args.floor)
    if reservationStatus["message"] == "Prenotazione confermata":
        print("Reservation confirmed on", str(args.day), "starting at", str(args.start), "ending at", str(args.end))
    else:
        print(reservationStatus["message"])


def print_logo() :
    print(" _    _   _   _   _____   __  __   _____")
    print("| |  | | | \\ | | |_   _| |  \\/  | |_   _|")
    print("| |  | | |  \\| |   | |   | \\  / |   | |")
    print("| |  | | | . ` |   | |   | |\\/| |   | |")
    print("| |__| | | |\\  |  _| |_  | |  | |  _| |_")
    print(" \\____/  |_| \\_| |_____| |_|  |_| |_____|\n")


if __name__ == "__main__":

    print_logo()

    parser = argparse.ArgumentParser(
        #prog = "Unimi library Reservation script",
        description = "Script for handling reservations at the BICF Library. Use '<command> -h' for details of an argument"
    )

    sub = parser.add_subparsers(required=True, dest = "subArgument")

    list = sub.add_parser("list", help="list of current reservable time slots on both floors")
    #biblio_l.add_argument("-piano", help="piano da visualizzare", required=True)
    list.set_defaults(func=list_library)

    book = sub.add_parser("book", help="reservation of the specified time slot on the chosen date")
    book.add_argument("-date", dest = "day", metavar = "YYYY-MM-DD", help="date of the reservation", required=True)
    book.add_argument("-floor", help="target floor", required=True, choices=["ground", "first"])
    book.add_argument("-start", metavar ="HH:MM" , help="reservation's start time, 24-hour format", required=True) # provare ad aggiungere type=datetime.strftime("%Y-%m-%d")
    book.add_argument("-end", metavar = "HH:MM", help="reservation's end time, 24-hour format", required=True)
    book.add_argument("-now", help="reserve your spot instantly rather than waiting until midnight", action=argparse.BooleanOptionalAction)
    #biblio_book.add_argument("-u", "--username", dest="u", metavar=None, help="email di istituto", required=True) #da aggiungere default, da sistemare metavar
    #biblio_book.add_argument("-p", "--password", dest="p", metavar=None, help="password di istituto", required=True)
    book.set_defaults(func=book_library)

    freespot = sub.add_parser("freespot", help="list of reservable time slots within a given timeframe on both floors; output also indicates whether the slots are already booked by the user")
    freespot.add_argument("-tf", metavar = "TIMEFRAME", help="input must be an integer representing the timeframe in hours (deafult is '1')", required=False, type=int, default=1)
    #biblio_freespot.add_argument("-day", help="giorno da visualizzare", required=True)
    #biblio_freespot.add_argument("-piano", help="piano da visualizzare", required=True)
    freespot.set_defaults(func=freespot_library)


    quick = sub.add_parser("quick", help="reserve your spot with default settings from config file")
    quick.add_argument("-now", help="reserve your spot instantly rather than waiting until midnight", action=argparse.BooleanOptionalAction)
    quick.set_defaults(func=book_library)

    args = parser.parse_args()
    args.func(args)