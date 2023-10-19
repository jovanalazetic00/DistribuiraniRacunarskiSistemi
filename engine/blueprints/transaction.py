from flask import Blueprint
import databaseCRUD
import flask
import threading
import MySQLdb

from multiprocessing import Queue
from time import sleep
from models.Transaction1 import Transaction1
from models.Transaction2 import Transaction2

queue = Queue()

transaction_blueprint = Blueprint('transaction_blueprint', __name__)


@transaction_blueprint.route('/getAllTransactionsForUser', methods=['GET'])
def getAllTransactionsForUser():
    content = flask.request.json
    _email = content['Email']
    _transactions = databaseCRUD.getAllTransactionsForUser(_email)

    return {'Transakcije': _transactions}, 200


@transaction_blueprint.route('/initTransaction1', methods=['POST'])
def initTransaction1():
    content = flask.request.json
    _sender = content['Posiljalac']  #stize sa fronta ko je posiljalac ko primalac
    _receiver = content['Primalac']
    _amount = content['Kolicina']
    _currency = content['Valuta']
    _rates = content['OdnosiZaKonverziju']
    _id = databaseCRUD.getLastTransactionId()  #dobavlja se id transakcije, povecan za jedan, jer se posle keiranja transakcije povecava za 1

    parametri = [_sender, _receiver, _amount, "U OBRADI", _currency]
    databaseCRUD.insertTransaction1(parametri)  #po parametrima, transakcija je u obradi

    _transakcija = Transaction1(_id, _sender, _receiver, _amount, _rates, _currency)  #objekat klase Transaction1

    thread = threading.Thread(target=transactionThread, args=(_transakcija,)) #kreiramo tred i saljemo argument transakcija
    thread.start()

    return "Ok"


@transaction_blueprint.route('/initTransaction2', methods=['POST'])
def initTransaction2():
    content = flask.request.json
    _senderEmail = content['Posiljalac']
    _receiverCardNumber = content['PrimalacBrojKartice']
    _amount = content['Kolicina']
    _currency = content['Valuta']
    _rates = content['OdnosiZaKonverziju']
    _id = databaseCRUD.getLastTransactionId()

    parametri = [_senderEmail, _receiverCardNumber, _amount, "U OBRADI", _currency]
    databaseCRUD.insertTransaction2(parametri)

    _transakcija = Transaction2(_id, _senderEmail, _receiverCardNumber, _amount, _rates, _currency)

    thread = threading.Thread(target=transactionThread, args=(_transakcija,))
    thread.start()

    return "Ok"


###############
#### METODE ###
###############

def transactionThread(transakcija):
    print('New thread started.')

    sleep(30)

    queue.put(transakcija)


def transactionProcess(queue: Queue):
    while 1:
        print("[PROCESS] Waiting for a new transaction")

        try:
            transaction = queue.get()
        except KeyboardInterrupt:  #ceka dok se ne ubaci tred
            break

        print(f"Transaction ID=[{transaction.transactionId}] started.")

        if isinstance(transaction, Transaction1): #provjerava koja je transakcija
            # Online - Online
            mydb = MySQLdb.connect(host="db", user="root", passwd="pass", db="DRS_PROJEKAT", port=3306)
            #konektujemo se sa bazom
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM Korisnik WHERE Korisnik.Email = %s", (transaction.sender,))
            #pisali posebno upite, jer je proces, pa ne dijeli memoriju, i ne vidi cursors
            _senderUser = cursor.fetchone()
            cursor.close()

            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM Korisnik WHERE Korisnik.Email = %s", (transaction.receiver,))
            _receiverUser = cursor.fetchone()   #dobavi posiljaoca i primaoca iz baze
            cursor.close()

            _oduzeti = 0

            if _senderUser is not None and _receiverUser is not None:

                if str(_senderUser[11]) == str(transaction.currency):
                    # Nije se menjala valuta posiljaoca
                    _oduzeti = transaction.senderAmount  #dobavili valutu korisnika koji je inicirao transakciju
                else:
                    # Promenila se valuta posiljaoca, neophodna konverzija
                    _oduzeti = float(transaction.senderAmount) * transaction.conversionRates[_senderUser[11]]

                _novoStanjePosiljaoca = _senderUser[9] - _oduzeti  #iz baze koliko imam oduzimam transakciju

                if _novoStanjePosiljaoca >= 0:
                    # Promeni stanje korisniku koji je uplatio novac
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE Korisnik SET NovcanoStanje = %s WHERE Email = %s ",
                                   (_novoStanjePosiljaoca, transaction.sender,))
                    cursor.close()

                    # Konvertovanje u valutu primaoca

                    _dodati = float(transaction.senderAmount) * transaction.conversionRates[_receiverUser[11]]

                    # Promeni stanje korisniku kojem se uplacuje novac

                    _novoStanjePrimaoca = _receiverUser[9] + _dodati
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE Korisnik SET NovcanoStanje = %s WHERE Email = %s ",
                                   (_novoStanjePrimaoca, transaction.receiver,))

                    cursor.close()

                    # Transakcija uspesna

                    cursor = mydb.cursor()
                    cursor.execute("UPDATE Transakcija SET StatusTransakcije = %s WHERE IdTransakcije = %s;",
                                   ("OBRADJENO", transaction.transactionId,))
                    mydb.commit()
                    cursor.close()

                else:
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE Transakcija SET StatusTransakcije = %s WHERE IdTransakcije = %s;",
                                   ("ODBIJENO", transaction.transactionId,))
                    mydb.commit()
                    cursor.close()

            else:
                cursor = mydb.cursor()
                cursor.execute("UPDATE Transakcija SET StatusTransakcije = %s WHERE IdTransakcije = %s;",
                               ("ODBIJENO", transaction.transactionId,))
                mydb.commit()
                cursor.close()

        elif isinstance(transaction, Transaction2):
            # Online - BankAccount
            mydb = MySQLdb.connect(host="db", user="root", passwd="pass", db="DRS_PROJEKAT", port=3306)

            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM Korisnik WHERE Korisnik.Email = %s", (transaction.sender,))
            _senderUser = cursor.fetchone()
            cursor.close()

            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM Kartica WHERE Kartica.BrojKartice = %s", (transaction.receiverCardNumber,))
            _receiverCard = cursor.fetchone()
            cursor.close()

            _oduzeti = 0

            if _senderUser is not None and _receiverCard is not None:
                if str(_senderUser[11]) == str(transaction.currency):
                    # Nije se menjala valuta posiljaoca
                    _oduzeti = transaction.senderAmount
                else:
                    # Promenila se valuta posiljaoca, neophodna konverzija
                    _oduzeti = float(transaction.senderAmount) * transaction.conversionRates[_senderUser[11]]

                _novoStanjePosiljaoca = _senderUser[9] - _oduzeti

                if _novoStanjePosiljaoca >= 0:
                    # Promeni stanje korisniku koji je uplatio novac
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE Korisnik SET NovcanoStanje = %s WHERE Email = %s ",
                                   (_novoStanjePosiljaoca, transaction.sender,))
                    cursor.close()

                    # Konvertovanje u valutu primaoca (Kartica je uvek dinarska)
                    if str(transaction.currency) == "RSD":
                        _dodati = float(transaction.senderAmount)
                    else:
                        _dodati = float(transaction.senderAmount) * transaction.conversionRates['RSD']

                    # Promeni stanje kartice na koju se uplacuje novac

                    _novoStanjePrimaoca = _receiverCard[3] + _dodati
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE Kartica SET NovcanoStanje = %s WHERE BrojKartice = %s ",
                                   (_novoStanjePrimaoca, transaction.receiverCardNumber,))

                    cursor.close()

                    # Transakcija uspesna

                    cursor = mydb.cursor()
                    cursor.execute("UPDATE Transakcija SET StatusTransakcije = %s WHERE IdTransakcije = %s;",
                                   ("OBRADJENO", transaction.transactionId,))
                    mydb.commit()
                    cursor.close()

                else:
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE Transakcija SET StatusTransakcije = %s WHERE IdTransakcije = %s;",
                                   ("ODBIJENO", transaction.transactionId,))
                    mydb.commit()
                    cursor.close()

            else:
                cursor = mydb.cursor()
                cursor.execute("UPDATE Transakcija SET StatusTransakcije = %s WHERE IdTransakcije = %s;",
                               ("ODBIJENO", transaction.transactionId,))
                mydb.commit()
                cursor.close()
