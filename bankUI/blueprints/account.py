from flask import Flask, Blueprint, render_template, request, json, redirect, url_for, session, flash
from time import sleep

import requests

account_blueprint = Blueprint('account_blueprint', __name__)


@account_blueprint.route('/account', methods=['GET'])  #da osvjezimo korisnika, svaki put kad nesto uradimo da se redirektujemo na account
#da ponovo ucita korisnika iz baze i ubaci u sesiju, da nam ne budu zastarjele informacije
def account():
    if 'user' not in session:   #ako user nije u sesiji vrati se na login
        return redirect(url_for('user_blueprint.login'))

    _email = session['user']['Email']  #izvadi ga iz sesije
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'email': _email})
    req = requests.post("http://engine:15002/user/refreshUser", data=body, headers=headers)
    response = (req.json())
    _code = req.status_code
    _user = response['user']
    session.permanent = False
    session['user'] = _user

    return render_template('nalog.html')


@account_blueprint.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user' not in session:
        return redirect(url_for('user_blueprint.login'))
    if request.method == 'GET':
        return render_template('izmenaProfila.html')
    elif request.method == 'POST':
        _ime = request.form['ime']
        _prezime = request.form['prezime']
        _adresa = request.form['adresa']
        _grad = request.form['grad']
        _drzava = request.form['drzava']
        _brTelefona = request.form['brojTelefona']
        _email = request.form['email']
        _lozinka = request.form['lozinka']
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        body = json.dumps({'ime': _ime, 'prezime': _prezime, 'adresa': _adresa, 'grad': _grad,
                           'drzava': _drzava, "brTelefona": _brTelefona, 'email': _email,
                           'oldEmail': session['user']['Email'], 'lozinka': _lozinka})
        req = requests.post("http://engine:15002/user/updateUser", data=body, headers=headers)
        response = (req.json())
        _code = req.status_code

        if _code == 200:
            body = json.dumps({'email': _email, 'password': _lozinka})
            req = requests.post("http://engine:15002/user/getUserByEmail", data=body, headers=headers)
            response = (req.json())
            _code = req.status_code

            if _code == 200:
                _user = response['user']
                session.permanent = False
                session['user'] = _user
                return redirect(url_for('account_blueprint.account'))
            else:
                return render_template("index.html")

        return redirect(url_for('account_blueprint.account'))


@account_blueprint.route('/verify', methods=['POST'])
def verify():
    if 'user' not in session:
        return redirect(url_for('user_blueprint.login'))

    _brKartice = request.form['brKartice']   #preuzimaju se parametri forme
    _ime = request.form['ime']
    _datum = request.form['datum']
    _kod = request.form['kod']
    _email = session['user']['Email']

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'brKartice': _brKartice, 'ime': _ime, 'datum': _datum, 'sigurnosniKod': _kod, 'email': _email})
    req = requests.post("http://engine:15002/user/updateUserCardNumber", data=body, headers=headers)
    response = (req.json())
    _code = req.status_code
    _message = response['message']

    if _code == 400:
        return render_template("nalog.html", message=_message)
    elif _code == 200:
        session['user']['Verifikovan'] = 1  #pristupamo pilju user i verifikovan u sesiji
        return redirect(url_for('account_blueprint.account'))


@account_blueprint.route('addMoney', methods=['POST'])
def addMoney():
    if 'user' not in session:
        return render_template("user_blueprint.login")

    if request.method == 'GET':
        return render_template('nalog.html')

    _email = session['user']['Email']
    _kolicinaOnline = request.form['unosNovca']

    URL = f"https://v6.exchangerate-api.com/v6/84da0ca6eca0cde00ef3f0ac/latest/{session['user']['Valuta']}"
    #mnozimo sa odnosom valuta
    r = requests.get(url=URL)
    data = r.json()

    _rate = data['conversion_rates']['RSD']
    _kolicina = float(_kolicinaOnline) * float(_rate)

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'Email': _email, 'KolicinaUDinarima': _kolicina, 'KolicinaOnline': _kolicinaOnline})  #saljemo kolicinu
    #u dinarima i online kolicinu
    req = requests.post("http://engine:15002/user/transferMoney", data=body, headers=headers)
    response = (req.json())
    _code = req.status_code
    _message = response['message']

    if _code == 400:
        return render_template("nalog.html", messageNoMoney=_message)
    elif _code == 200:
        _stanje = response['stanje']
        session['user']['NovcanoStanje'] = _stanje
        return redirect(url_for('account_blueprint.account'))


@account_blueprint.route('changeCurrency', methods=['POST'])
def changeCurrency():
    if 'user' not in session:
        return render_template("user_blueprint.login")

    if request.method == 'GET':
        return render_template('nalog.html')

    _valutaTrenutna = session['user']['Valuta']
    _novcanoStanjeTrenutno = session['user']['NovcanoStanje']
    _email = session['user']['Email']

    URL = f"https://v6.exchangerate-api.com/v6/84da0ca6eca0cde00ef3f0ac/latest/{_valutaTrenutna}"
    r = requests.get(url=URL)
    data = r.json()

    _valutaUKojuPrebacujem = request.form['valuta2']
    _rate = data['conversion_rates'][f'{_valutaUKojuPrebacujem}']

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'Rate': _rate, 'ValutaUKojuPrebacujem': _valutaUKojuPrebacujem, 'Email': _email})
    req = requests.post("http://engine:15002/user/changeCurrency", data=body, headers=headers)
    response = (req.json())
    _code = req.status_code
    _convertedValue = response['ConvertedValue']
    session['user']['Valuta'] = _valutaUKojuPrebacujem
    session['user']['NovcanoStanje'] = _convertedValue

    return redirect(url_for('account_blueprint.account'))


@account_blueprint.route('showTransactionHistory', methods=['GET'])
def showTransactionHistory():
    _email = session['user']['Email']

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'Email': _email})
    req = requests.get("http://engine:15002/transaction/getAllTransactionsForUser", data=body, headers=headers)
    response = (req.json())
    _code = req.status_code
    _transactions = response['Transakcije']

    return render_template("history.html", podaci=_transactions)


@account_blueprint.route('transactionOnline', methods=['GET', 'POST'])
def transactionOnline():   #sa online racuna na drugi online racun
    _emailPosiljaoca = session['user']['Email']
    _valuta = session['user']['Valuta']
    _emailPrimaoca = request.form['emailPrimaoca']
    _kolicinaOnline = request.form['kolicinaZaOnline']

    URL = f"https://v6.exchangerate-api.com/v6/84da0ca6eca0cde00ef3f0ac/latest/{_valuta}"
    r = requests.get(url=URL)
    data = r.json()
    _odnosiZaKonverziju = data['conversion_rates']

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'Posiljalac': _emailPosiljaoca, 'Primalac': _emailPrimaoca, 'Kolicina': float(_kolicinaOnline),
         'Valuta': _valuta, 'OdnosiZaKonverziju': _odnosiZaKonverziju})
    req = requests.post("http://engine:15002/transaction/initTransaction1", data=body, headers=headers)
    _code = req.status_code

    return redirect(url_for('account_blueprint.account'))


@account_blueprint.route('transactionCard', methods=['GET', 'POST'])
def transactionCard():
    _emailPosiljaoca = session['user']['Email']
    _valuta = session['user']['Valuta']
    _brKartice = request.form['brKarticePrimaoca']
    _kolicinaCard = request.form['kolicinaZaCard']

    URL = f"https://v6.exchangerate-api.com/v6/84da0ca6eca0cde00ef3f0ac/latest/{_valuta}"
    r = requests.get(url=URL)
    data = r.json()
    _odnosiZaKonverziju = data['conversion_rates']

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'Posiljalac': _emailPosiljaoca, 'PrimalacBrojKartice': _brKartice, 'Kolicina': float(_kolicinaCard),
         'Valuta': _valuta, 'OdnosiZaKonverziju': _odnosiZaKonverziju})
    req = requests.post("http://engine:15002/transaction/initTransaction2", data=body, headers=headers)
    _code = req.status_code

    return redirect(url_for('account_blueprint.account'))
