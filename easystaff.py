import re
import json
import config

import requests
from bs4 import BeautifulSoup as bs
from datetime import date, datetime

from exceptions import(
        EasystaffLoginForm,
        EasystaffLogin,
        EasystaffBookingPage,
        EasystaffBooking,
        EasystaffBiblio,
        EasystaffBiblioPersonal
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

RESERVATION_INPUT = {"cliente": "biblio", "start_time": {}, "end_time": {}, "durata": {}, "entry_type": 92, "area": 25, "public_primary": config.CODICEFISCALE, "utente": {"codice_fiscale": config.CODICEFISCALE, "cognome_nome": config.COGNOMENOME, "email": config.EMAIL}, "servizio": {}, "risorsa": None, "recaptchaToken": None, "timezone": "Europe/Rome"}

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
        payload["username"] = config.EMAIL
        payload["password"] = config.PASSWORD

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
    

    def get_freespot(self, timeframe:int):
        res = self._session.get(LIBRARY_URL_GROUND_PERSONAL.format(date.today(), str(timeframe*3600), config.CODICEFISCALE))
        if not res.ok:
            raise EasystaffBiblioPersonal(f"Failed to fetch your library reservations page, responded with {res.status_code}")
        groundLibrary = json.loads(res.text)


        res = self._session.get(LIBRARY_URL_FIRST_PERSONAL.format(date.today(), str(timeframe*3600), config.CODICEFISCALE))
        if not res.ok:
            raise EasystaffBiblioPersonal(f"Failed to fetch your library reservations page, responded with {res.status_code}")
        firstLibrary = json.loads(res.text)

        return groundLibrary, firstLibrary


    def get_book(self, day:str, start:str, end:str, floor:str):

        day = datetime.strptime(day, "%Y-%m-%d")
        day = int(day.timestamp())
        start, half = start.split(":")
        start = int(start)*3600
        if half != "00" :
            start += 1800
        end, half = end.split(":")
        end = int(end)*3600
        if half != "00" :
            end += 1800 
        start = day+start
        end = day+end

        RESERVATION_INPUT["start_time"]=day+start
        RESERVATION_INPUT["end_time"]=day+end
        RESERVATION_INPUT["duarata"]=(day+start)-(day+end)
        res = self._session.post(LIBRARY_BOOK, json=RESERVATION_INPUT)
        if not res.ok:
            raise EasystaffBookingPage(f"Failed to reserve your spot, responded with {res.status_code}")
        response_json = res.json()
        id = response_json["entry"]
        res = self._session.post(CONFIRM_LIBRARY_BOOKING.format(id))
        print(res.text)
        if not res.ok:
            raise EasystaffBooking(f"Failed to reserve your spot, responded with {res.status_code}")