import argparse, pytz, json, os
from time import sleep
from datetime import datetime, date
from inspect import getsourcefile
from os.path import abspath
from UnimiLibrary.easystaff import Easystaff

def wait_start():
    startTime = "07:05"
    startTime = datetime.strptime(startTime, "%H:%M").time()
    limitTime = "06:55"
    limitTime = datetime.strptime(limitTime, "%H:%M").time()
    cet = pytz.timezone("CET")

    while not (limitTime <= datetime.now(cet).time() <= startTime):
        sleep(120)


def setupConfigFile(args):

    # for loc in os.curdir, os.path.expanduser("~"), "/etc/UnimiLibrary", os.environ.get("UnimiLibrary_CONF"):  
    #     try:
    #         with open(os.path.join(loc,'config.json'), 'r') as config_file:
    #             data = json.load(config_file)
    #             if data:
    #                 break
    #     except FileNotFoundError:
    #         data = {}

    dir_path = abspath(getsourcefile(lambda:0)).removesuffix(os.path.basename(__file__))
    dir_path = os.path.join(dir_path,'config.json')
    try:
        with open(dir_path, 'r') as config_file:
            data = json.load(config_file)
    except FileNotFoundError:
        data = {}

    config_mappings = {
        "name": "NAME",
        "email": "EMAIL",
        "password": "PASSWORD",
        "cf": "CODICEFISCALE",
        "start": "START",
        "end": "END",
        "floor": "FLOOR"
    }

    for arg, config_key in config_mappings.items():
        arg_value = getattr(args, arg, None)
        if arg_value:
            data[config_key] = arg_value

    # if args.name:
    #     data["NAME"] = args.name
    # if args.email:
    #     data["EMAIL"] = args.email
    # if args.password:
    #     data["PASSWORD"] = args.password
    # if args.cf:
    #     data["CODICEFISCALE"] = args.cf
    # if args.start:
    #     data["START"] = args.start
    # if args.end:
    #     data["END"] = args.end
    # if args.floor:
    #     data["FLOOR"] = args.floor

    with open(dir_path, 'w') as config_file:
        json.dump(data, config_file, indent=4)


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
            alreadyListed = []
            for j in firstLibrary[i]:
                if j not in alreadyListed:
                    alreadyListed.append(j)
                    print("-", j)

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
                print("-", timeslot, "| active reservation:", reservation["reserved"])


def book_library(args):

    if not args.now :
        wait_start()

    a = Easystaff()
    a.login()
    reservationStatus = a.get_book(args)
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

    config = sub.add_parser("config", help="configure config file's values")
    config.add_argument("-name", help = "last name + first name, first letter uppercase, wrapped in double quotes (ex: \"Rossi Mario\")")
    config.add_argument("-email", help = "Unimi institutional email")
    config.add_argument("-password", help = "Unimi account password")
    config.add_argument("-cf", help = "codicefiscale, must be uppercase")
    config.add_argument("-start", metavar = "HH:MM", help="reservation's end time, 24-hour format")
    config.add_argument("-end", metavar = "HH:MM", help = "reservation's start time, 24-hour format")
    config.add_argument("-floor", help="target floor", choices=["ground", "first"])
    config.set_defaults(func=setupConfigFile)

    args = parser.parse_args()
    args.func(args)