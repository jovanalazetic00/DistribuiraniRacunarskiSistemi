from app import db


def getByEmail(email: str) -> dict:
    _query = "SELECT * FROM Korisnik WHERE Korisnik.Email = %(email)s"  #kveri gdje je email jednak emailu koji smo proslijedili funkciji

    try:
        with db.connection.cursor() as cursor:  #konektujemo se sa kursorom na bazu
            cursor.execute(_query, {'email': email})  #izvrsimo
            _user = cursor.fetchone()  #fetchone dobavlja prvog kog nadje
            cursor.close()

            return _user  #vrati nam usera
    except NameError:
        print(NameError.name)

        return {}.get('missing_key', None)


def insert(args) -> dict:
    if len(args) > 12:
        return -5

    _ime = args[0]
    _prezime = args[1]
    _adresa = args[2]
    _grad = args[3]
    _drzava = args[4]
    _brTelefona = args[5]
    _email = args[6]
    _lozinka = args[7]
    _brKartice = args[8]
    _novcanoStanje = args[9]
    _verifikovan = args[10]
    _valuta = args[11]

    _query = """INSERT INTO Korisnik (Ime, Prezime, Adresa, Grad, Drzava, BrojTelefona, Email, Lozinka, BrojKartice, 
    NovcanoStanje, Verifikovan, Valuta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); """  #ubacujemo u korisnik

    try:
        with db.connection.cursor() as cursor:
            data = (_ime, _prezime, _adresa, _grad, _drzava, _brTelefona, _email, _lozinka, _brKartice, _novcanoStanje,
                    _verifikovan, _valuta)
            cursor.execute(_query, data)   #zbog metode into korisnik, radi se connection i commit
            db.connection.commit()
    except NameError:
        print(NameError.name)

        return {}.get('missing_key', None)


def deleteByEmail(email) -> dict:
    _query = "DELETE FROM Korisnik WHERE Korisnik.Email = %(email)s"

    try:
        with db.connection.cursor() as cursor:
            cursor.execute(_query, {'email': email})
            db.connection.commit()
    except NameError:
        print(NameError.name)
        return {}.get('missing_key', None)


def update(args) -> dict:
    if len(args) > 9:
        return -5

    _ime = args[0]
    _prezime = args[1]
    _adresa = args[2]
    _grad = args[3]
    _drzava = args[4]
    _brTelefona = args[5]
    _email = args[6]
    _lozinka = args[7]
    _oldEmail = args[8]

    _query = """UPDATE Korisnik SET Ime = %s, Prezime = %s, Adresa = %s, Grad = %s, Drzava = %s,
     BrojTelefona = %s, Email = %s, Lozinka = %s WHERE Email = %s """
    try:
        with db.connection.cursor() as cursor:
            data = (_ime, _prezime, _adresa, _grad, _drzava, _brTelefona, _email, _lozinka, _oldEmail)
            cursor.execute(_query, data)
            db.connection.commit()
    except NameError:
        print(NameError.name)

        return {}.get('missing_key', None)


def updateUserBalance(args) -> dict:
    if len(args) > 2:
        return -5

    _email = args[0]
    _novac = args[1]

    _query = """UPDATE Korisnik SET NovcanoStanje = %s WHERE Email = %s """
    try:
        with db.connection.cursor() as cursor:
            data = (_novac, _email)
            cursor.execute(_query, data)
            db.connection.commit()
    except NameError:
        print(NameError.name)

        return {}.get('missing_key', None)


def updateUserBalanceAndCurrency(args) -> dict:
    if len(args) > 3:
        return -5

    _email = args[0]
    _novac = args[1]
    _valuta = args[2]

    _query = """UPDATE Korisnik SET NovcanoStanje = %s, Valuta = %s WHERE Email = %s """
    try:
        with db.connection.cursor() as cursor:
            data = (_novac, _valuta, _email)
            cursor.execute(_query, data)
            db.connection.commit()
    except NameError:
        print(NameError.name)

        return {}.get('missing_key', None)


def updateCardNumber(args) -> dict:
    if len(args) > 2:
        return -5

    _brKartice = args[0]
    _email = args[1]

    _query = """UPDATE Korisnik SET BrojKartice = %s, Verifikovan = %s WHERE Email = %s """
    try:
        with db.connection.cursor() as cursor:
            data = (_brKartice, 1, _email)
            cursor.execute(_query, data)
            db.connection.commit()
    except NameError:
        print(NameError.name)

        return {}.get('missing_key', None)
