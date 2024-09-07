class Easystaff(Exception):
    "An exception raised when there's an easystaff related error"
    pass

class EasystaffLoginForm(Easystaff):
    "An exception raised when the cas.unimi.it login form couldn't be retrieved"
    pass

class EasystaffLogin(Easystaff):
    "An exception raised when the login fails"
    pass

class EasystaffBookingPage(Easystaff):
    "An exception raised when fetching the reservation page"
    pass

class EasystaffBooking(Easystaff):
    "An exception raised when confirming your reservation"
    pass

class EasystaffBiblio(Easystaff):
    "An exception raised when fetching the libaray page"
    pass

class EasystaffBiblioPersonal(Easystaff):
    "An exception raised when trying to fetch your library page"
    pass