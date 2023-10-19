from flask import Blueprint
import databaseCRUD
import flask

card_blueprint = Blueprint('card_blueprint', __name__)


@card_blueprint.route('/getCardByNumber', methods=['GET'])
def getCard():
    content = flask.request.json
    _brojKartice = content['BrojKartice']

    _card = databaseCRUD.getByNumber(_brojKartice)

    return {'Card': _card}, 200


@card_blueprint.route('/insertCard', methods=['POST'])
def insertCard():
    # insertovanje kartice u bazu
    content = flask.request.json
    brojKartice = content['BrojKartice']
    imeKorisnika = content['ImeKorisnika']
    datumIsteka = content['DatumIsteka']
    novcanoStanje = content['NovcanoStanje']
    sigurnosniKod = content['SigurnosniKod']
    parametri = [brojKartice, imeKorisnika, datumIsteka, novcanoStanje, sigurnosniKod]

    databaseCRUD.insertC(parametri)

    return "Ok"


@card_blueprint.route('/deleteCardByNumber', methods=['DELETE'])
def deleteCardByNumber():
    content = flask.request.json
    brojKartice = content['BrojKartice']
    databaseCRUD.deleteByNumber(brojKartice)

    return "Ok"


@card_blueprint.route('/updateCard', methods=['POST'])
def updateCard():
    content = flask.request.json
    brojKartice = content['BrojKartice']
    imeKorisnika = content['ImeKorisnika']
    datumIsteka = content['DatumIsteka']
    novcanoStanje = content['NovcanoStanje']
    sigurnosniKod = content['SigurnosniKod']
    parametri = [brojKartice, imeKorisnika, datumIsteka, novcanoStanje, sigurnosniKod]

    databaseCRUD.updateC(parametri)

    return "Ok"
