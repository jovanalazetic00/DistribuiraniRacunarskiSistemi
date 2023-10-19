from flask import Blueprint
import databaseCRUD
import flask

user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route('/getUserByEmail', methods=['GET', 'POST'])
def getUser():
    # TO DO: get user by email
    content = flask.request.json
    _email = content['email']  #email i lozinku uzmemo iz contenta
    _password = content['password']

    _user = databaseCRUD.getByEmail(_email)  #dobavimo korisnika iz baze

    if _user is not None:
        if _password == _user['Lozinka']:
            return {'user': _user, 'message': 'Uspešno ulogovan!'}, 200
        else:
            return {'message': 'Pogrešna lozinka!'}, 400
    return {'message': 'Korisnik ne postoji!'}, 400


@user_blueprint.route('/refreshUser', methods=['GET', 'POST'])
def refreshUser():

    content = flask.request.json
    _email = content['email']

    _user = databaseCRUD.getByEmail(_email)

    return {'user': _user}, 200


@user_blueprint.route('/insertUser', methods=['POST'])
def insertUser():     #iscitivamo, uzimamo iz kontenta
    # insertovanje korisnika u bazu
    content = flask.request.json  #kontent je request json
    ime = content['ime']
    prezime = content['prezime']   #preuzimamo parametre, na osnovu kljuca dobijemo vrijednost
    adresa = content['adresa']
    grad = content['grad']
    drzava = content['drzava']
    brTel = content['brTelefona']
    email = content['email']
    lozinka = content['lozinka']
    brojKartice = 0
    novcanoStanje = 0  # inicijalne vrijednosti, kad se korisnik registruje, prije verifikacije
    verifikovan = 0
    valuta = "RSD"
    parametri = [ime, prezime, adresa, grad, drzava, brTel, email, lozinka, brojKartice, novcanoStanje, verifikovan,
                 valuta]  #saljemo parametre spakovane u listu

    _user = databaseCRUD.getByEmail(email)

    if _user is None:  #ako nije nasao usera
        databaseCRUD.insert(parametri)  #ubaci ga u bazu
        return {'message': 'Korisnik uspesno registrovan!'}, 200
    return {'message': 'Korisnik vec postoji!'}, 400


@user_blueprint.route('/deleteUserByEmail', methods=['DELETE'])
def deleteUserByEmail():
    content = flask.request.json
    email = content['Email']
    databaseCRUD.deleteByEmail(email)

    return "Ok"


@user_blueprint.route('/updateUser', methods=['POST'])
def updateUserCardNumber():
    content = flask.request.json
    ime = content['ime']
    prezime = content['prezime']
    adresa = content['adresa']
    grad = content['grad']
    drzava = content['drzava']
    brTel = content['brTelefona']
    email = content['email']
    lozinka = content['lozinka']
    oldEmail = content['oldEmail']

    parametri = [ime, prezime, adresa, grad, drzava, brTel, email, lozinka, oldEmail]

    databaseCRUD.update(parametri)

    return {'message': 'Korisnik uspesno izmenjen!'}, 200


@user_blueprint.route('/updateUserCardNumber', methods=['POST'])
def updateUser():
    content = flask.request.json
    brKartice = content['brKartice']  #uzmem iz contenta sve sa bankUI
    ime = content['ime']
    datumIsteka = content['datum']
    sigurnosniKod = content['sigurnosniKod']
    email = content['email']

    _card = databaseCRUD.getByNumber(brKartice)

    if _card is None:
        return {'message': 'Kartica ne postoji.'}, 400
    else:
        if _card['ImeKorisnika'] != ime:
            return {'message': 'Pogrešno ime.'}, 400
        elif _card['DatumIsteka'].strftime("%Y-%m-%d") != datumIsteka:
            return {'message': 'Pogrešan datum.'}, 400
        elif str(_card['SigurnosniKod']) != sigurnosniKod:
            return {'message': 'Pogrešan kod.'}, 400
        elif (_card['NovcanoStanje'] - 100) < 0:  #skidamo dolar posle verifikacije
            return {'message': 'Nedovoljno sredstva.'}, 400

        parametri = [brKartice, email]  #kad se verifikuje dodijeli mu se br kartice

        databaseCRUD.updateCardNumber(parametri)

        newBalance = _card['NovcanoStanje'] - 100
        parametri = [brKartice, newBalance]
        databaseCRUD.decreaseBalance(parametri)  #da se smanji novcano stanje

        return {'message': 'Korisnik uspesno verifikovan!'}, 200


@user_blueprint.route('/transferMoney', methods=['POST'])
def transferMoney():
    content = flask.request.json
    email = content['Email']
    kolicinaUDinarima = content['KolicinaUDinarima']  #preuzmemo sto je korisnik poslao
    kolicinaOnline = content['KolicinaOnline']

    _user = databaseCRUD.getByEmail(email)
    _card = databaseCRUD.getByNumber(_user['BrojKartice'])  #pristupamo kartici

    if float(kolicinaUDinarima) > _card['NovcanoStanje']:
        return {'message': 'Nemate dovoljno novca na kartici.'}, 400

    _user['NovcanoStanje'] = _user['NovcanoStanje'] + float(kolicinaOnline)  #povecamo online racun
    _card['NovcanoStanje'] = _card['NovcanoStanje'] - float(kolicinaUDinarima)  #smanjimo sa kartice

    parametri1 = [_card['BrojKartice'], _card['ImeKorisnika'], _card['DatumIsteka'],
                  _card['NovcanoStanje'], _card['SigurnosniKod']]
    parametri2 = [_user['Email'], _user['NovcanoStanje']]
    databaseCRUD.updateC(parametri1)
    databaseCRUD.updateUserBalance(parametri2)

    return {'message': 'Novac sa kartice na online racun uspesno prebacen!', 'stanje': _user['NovcanoStanje']}, 200


@user_blueprint.route('/changeCurrency', methods=['POST'])
def changeCurrency():
    content = flask.request.json
    _rate = content['Rate']
    _valutaUKojuPrebacujem = content['ValutaUKojuPrebacujem']
    _email = content['Email']

    _user = databaseCRUD.getByEmail(_email)
    _convertedValue = _user['NovcanoStanje'] * _rate  #novcano stanje puta rate-odnos valuta
    _user['NovcanoStanje'] = _convertedValue
    _user['Valuta'] = _valutaUKojuPrebacujem
    parametri = [_user['Email'], _user['NovcanoStanje'], _user['Valuta']]

    databaseCRUD.updateUserBalanceAndCurrency(parametri)

    return {'ConvertedValue': _convertedValue}, 200
