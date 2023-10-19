from flask import Flask, Blueprint, render_template, request, json, session, redirect, url_for, make_response
from time import sleep
import requests

user_blueprint = Blueprint('user_blueprint', __name__)  #da razdvojim endpointe po smislu sta treba da rade


@user_blueprint.route('/')
def index():

    return render_template('index.html')


@user_blueprint.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('index.html')
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
        #heder zaglavlje koje saljem beku, da on zna da je to json objekat i da prihvata tekst i plein
        body = json.dumps({'ime': _ime, 'prezime': _prezime, 'adresa': _adresa, 'grad': _grad,
                           'drzava': _drzava, "brTelefona": _brTelefona, 'email': _email, 'lozinka': _lozinka})
        #formira se json objekat koji saljemo flask aplikaciji engine, json je javascript objektna notacija
        req = requests.post("http://engine:15002/user/insertUser", data=body, headers=headers) #gadjamo back
        response = (req.json())
        print(response)
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
        else:
            return render_template("index.html")


@user_blueprint.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        _email = request.form['email']
        _password = request.form['password']   #iz forme uzimamo sta je korisnik unio

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        body = json.dumps({'email': _email, 'password': _password})
        req = requests.post("http://engine:15002/user/getUserByEmail", data=body, headers=headers)
        response = (req.json())  #trazimo odgovor u json formatu
        _code = req.status_code
        _message = response['message']

        if _code == 200:  #ako je kod uspjesan
            _user = response['user']  #izvadimo korisnika iz responsa
            session.permanent = False  #sesija nije trajna
            session['user'] = _user  #stavimo korisnika u sesiju
            return redirect(url_for('account_blueprint.account'))
        else:
            return render_template('login.html', message=_message)


@user_blueprint.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    return redirect(url_for('user_blueprint.login'))  #izbaci korisnika iz sesije
