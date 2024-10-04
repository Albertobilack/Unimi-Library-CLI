import json, requests, os, sys
from bs4 import BeautifulSoup as bs
from datetime import date, datetime, timedelta
from inspect import getsourcefile
from os.path import abspath

from UnimiLibrary.exceptions import(
        EasystaffLoginForm,
        EasystaffLogin,
        EasystaffBookingPage,
        EasystaffBooking,
        EasystaffBiblio,
        EasystaffBiblioPersonal,
)


FORM_URL = "https://orari-be.divsi.unimi.it/EasyAcademy/auth/auth_app.php??response_type=token&client_id=client&redirect_uri=https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=login&scope=openid+profile"
LOGIN_URL = "https://cas.unimi.it/login"
EASYSTAFF_LOGIN_URL = "https://easystaff.divsi.unimi.it/PortaleStudenti/login.php?from=&from_include="

#date YYYY, date MM, timeframe timeframe (3600 is equal to an hour, 1800 half an hour)
LIBRARY_URL_FIRST  = "https://prenotabiblio.sba.unimi.it/portalePlanningAPI/api/entry/50/schedule/{}-{}/25/{}"
LIBRARY_URL_GROUND = "https://prenotabiblio.sba.unimi.it/portalePlanningAPI/api/entry/92/schedule/{}-{}/25/{}"

#date YYYY-MM-DD, timeframe (3600 is equal to an hour, 1800 half an hour), cf uppercase
LIBRARY_URL_FIRST_PERSONAL = "https://prenotabiblio.sba.unimi.it/portalePlanningAPI/api/entry/50/schedule/{}/25/{}?user_primary={}"
LIBRARY_URL_GROUND_PERSONAL = "https://prenotabiblio.sba.unimi.it/portalePlanningAPI/api/entry/92/schedule/{}/25/{}?user_primary={}"

LIBRARY_BOOK = "https://prenotabiblio.sba.unimi.it/portalePlanningAPI/api/entry/store"
CONFIRM_LIBRARY_BOOKING = "https://prenotabiblio.sba.unimi.it/portalePlanningAPI/api/entry/confirm/{}"

RESERVATION_INPUT = {"cliente": "biblio", "start_time": {}, "end_time": {}, "durata": {}, "entry_type": {}, "area": 25, "public_primary": {}, "utente": {"codice_fiscale": {}, "cognome_nome": {}, "email": {}}, "servizio": {}, "risorsa": None, "recaptchaToken": None, "timezone": "Europe/Rome"}


def readConfig(valuesRequested):
    
    #dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    #dir_path = os.path.abspath(os.path.dirname(__file__))
    dir_path = abspath(getsourcefile(lambda:0)).removesuffix(os.path.basename(__file__))
    try:
        with open(os.path.join(dir_path,'config.json'), 'r') as config_file:
            data = json.load(config_file)
    except FileNotFoundError:
        print("please setup config file running python -m UnimiLibrary config")
        sys.exit(0)

    if type(valuesRequested) == str:
        return data[valuesRequested]

    configOutput = ()
    for value in valuesRequested:
        configOutput = configOutput + (data[value],)
    
    return configOutput


def configQuick(args):
    if args.now :
        today = datetime.today()
        args.day = today.strftime("%Y-%m-%d")
    else:
        today = datetime.today() + timedelta(days=1)
        args.day = today.strftime("%Y-%m-%d")
    args.start, args.end, args.floor = readConfig(("START", "END", "FLOOR"))


def setupReservationInput(args):
    if args.subArgument == "quick":
            configQuick(args)

    day = datetime.strptime(args.day, "%Y-%m-%d")
    day = int(day.timestamp())
    start, half = args.start.split(":")
    start = int(start)*3600
    if half == "30" :
        start += 1800
    end, half = args.end.split(":")
    end = int(end)*3600
    if half == "30" :
        end += 1800

    if args.floor == "ground":
        entryType = 92
    elif args.floor == "first":
        entryType = 50

    config = readConfig(["CODICEFISCALE", "NAME", "EMAIL"])
    
    RESERVATION_INPUT.update({
        "start_time": day + start,
        "end_time": day + end,
        "durata": end - start,
        "entry_type": entryType,
        "public_primary": config[0],
        "utente": {
            "codice_fiscale": config[0],
            "cognome_nome": config[1],
            "email": config[2]
        }
    })


class Easystaff:
    def __init__(self):
        self._token = None
        self._session = requests.Session()


    def _get_login_form(self):
        res = self._session.get(FORM_URL)
        if not res.ok:
            raise EasystaffLoginForm(f"Couldn't fetch CAS form, responded with {res.status_code}")

        form_data = {
                "selTipoUtente": "S",
                "hCancelLoginLink": "http://www.unimi.it",
                "hForgotPasswordLink": "https://auth.unimi.it/password/",
                "service": "https://orari-be.divsi.unimi.it/EasyAcademy/auth/auth_app.php??response_type=token&client_id=client&redirect_uri=https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=login&scope=openid+profile",
                "_eventId": "submit",
                "_responsive": "responsive",
        }

        form_soup = bs(res.text, "lxml")
        lt = form_soup.find_all(id="hLT")[0]["value"]
        execution = form_soup.find_all(id="hExecution")[0]["value"]

        form_data["lt"] = lt
        form_data["execution"] = execution
        return form_data


    def login(self):
        payload = self._get_login_form()
        payload["username"] = readConfig("EMAIL")
        payload["password"] = readConfig("PASSWORD")

        res = self._session.post(LOGIN_URL, data=payload)
        if not res.ok:
            raise EasystaffLogin(f"Failed to login, responded with {res.status_code}")
        
        token_url = res.text[48:348]
        token_url = token_url[token_url.find("access_token") + 13:]
        res = self._session.post(
                EASYSTAFF_LOGIN_URL,
                data={"access_token": token_url}
        )
        if not res.ok:
            raise EasystaffLogin(f"Failed on access token, responded with {res.status_code}")


    def get_list(self):
        currentDate = date.today()
        year = currentDate.strftime("%Y")
        month = currentDate.strftime("%m")

        res = self._session.get(LIBRARY_URL_GROUND.format(year, month, "3600"))
        if not res.ok:
            raise EasystaffBiblio(f"Failed to fetch the library avaible spot, responded with {res.status_code}")
        groundLibrary = json.loads(res.text)

        res = self._session.get(LIBRARY_URL_FIRST.format(year, month, "3600")) 
        if not res.ok:
            raise EasystaffBiblio(f"Failed to fetch the library avaible spot, responded with {res.status_code}")
        firstLibrary = json.loads(res.text)

        return groundLibrary, firstLibrary
    
#res if no avabile spot :{'schedule': {"YYYY-MM-DD": {}}}
#res if day is not avaible : {'schedule': []}
    def get_freespot(self, timeframe:int):
        
        dayOne = date.today()
        dayTwo = dayOne + timedelta(days=1)
        dayThree = dayOne + timedelta(days=2)
        dayFour = dayOne + timedelta(days=3)
        codiceFiscale = readConfig("CODICEFISCALE")

        # dayOne = date.today()
        # addOneDay = timedelta(days=1)
        # dayTwo = dayOne + addOneDay
        # dayThree = dayTwo + addOneDay
        # dayFour = dayThree + addOneDay

        groundLibrary = {"schedule": {}}

        res = self._session.get(LIBRARY_URL_GROUND_PERSONAL.format(dayOne, str(timeframe*3600), codiceFiscale))
        if not res.ok:
            raise EasystaffBiblioPersonal(f"Failed to fetch your library reservations page, responded with {res.status_code}")
        firstDay = json.loads(res.text)
        if str(dayOne) in firstDay["schedule"]:
            groundLibrary["schedule"][str(dayOne)] = firstDay["schedule"][str(dayOne)]
        # else:
        #     groundLibrary["schedule"][str(dayOne)] = {}

        res = self._session.get(LIBRARY_URL_FIRST_PERSONAL.format(dayOne, str(timeframe*3600), codiceFiscale))
        if not res.ok:
            raise EasystaffBiblioPersonal(f"Failed to fetch your library reservations page, responded with {res.status_code}")
        firstLibrary = json.loads(res.text)

        res = self._session.get(LIBRARY_URL_GROUND_PERSONAL.format(dayTwo, str(timeframe*3600), codiceFiscale))
        if not res.ok:
            raise EasystaffBiblioPersonal(f"Failed to fetch your library reservations page, responded with {res.status_code}")
        secondDay = json.loads(res.text)
        if str(dayTwo) in secondDay["schedule"]:
            groundLibrary["schedule"][str(dayTwo)] = secondDay["schedule"][str(dayTwo)]
        # else:
        #     groundLibrary["schedule"][str(dayThree)] = {}

        res = self._session.get(LIBRARY_URL_GROUND_PERSONAL.format(dayThree, str(timeframe*3600), codiceFiscale))
        if not res.ok:
            raise EasystaffBiblioPersonal(f"Failed to fetch your library reservations page, responded with {res.status_code}")
        thirdDay = json.loads(res.text)
        if str(dayThree) in thirdDay["schedule"]:
            groundLibrary["schedule"][str(dayThree)] = thirdDay["schedule"][str(dayThree)]
        # else:
        #     groundLibrary["schedule"][str(dayThree)] = {}

        res = self._session.get(LIBRARY_URL_GROUND_PERSONAL.format(dayFour, str(timeframe*3600), codiceFiscale))
        if not res.ok:
            raise EasystaffBiblioPersonal(f"Failed to fetch your library reservations page, responded with {res.status_code}")
        fourthDay = json.loads(res.text)
        if str(dayFour) in fourthDay["schedule"]:
            groundLibrary["schedule"][str(dayFour)] = fourthDay["schedule"][str(dayFour)]
        # else:
        #     groundLibrary["schedule"][str(dayFour)] = {}

        return groundLibrary, firstLibrary


    #DO NOT USE DATE INSTEAD OF DAY
    def get_book(self, args):

        setupReservationInput(args)

        res = self._session.post(LIBRARY_BOOK, json=RESERVATION_INPUT)
        if not res.ok:
            raise EasystaffBookingPage(f"Failed to reserve your spot, responded with {res.status_code}")
        response_json = res.json()
        id = response_json["entry"]
        res = self._session.post(CONFIRM_LIBRARY_BOOKING.format(id))
        if not res.ok:
            raise EasystaffBooking(f"Failed to reserve your spot, responded with {res.status_code}")
        reservationStatus = json.loads(res.text)
        return reservationStatus