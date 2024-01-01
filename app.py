# Store this code in 'app.py' file
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pdfkit


app = Flask(__name__)


app.secret_key = 'your secret key'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'Pharmacy'


mysql = MySQL(app)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'Empid' in request.form and 'password' in request.form:
		Empid = request.form['Empid']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute(
			'SELECT * FROM Accounts WHERE Empid = %s AND password = MD5(%s)', (Empid, password, ))
		Account = cursor.fetchone()
		if Account:
			session['loggedin'] = True
			session['Empid'] = Account['Empid']
			msg = 'Logged in successfully !'
			return render_template('index.html', msg=msg)
		else:
			msg = 'Incorrect Empid / password !'
	return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('Empid', None)
	return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])

def register():
	msg = ''
	if request.method == 'POST' and 'Empid' in request.form and 'password' in request.form and 'email' in request.form :
		Empid = request.form['Empid']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute(
			'SELECT * FROM Accounts WHERE Empid = % s', (Empid, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', Empid):
			msg = 'name must contain only characters and numbers !'
		else:
			cursor.execute('INSERT INTO Accounts(Empid,password,email) VALUES ( % s, MD5(% s), % s )', (Empid, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg=msg)


@app.route("/update", methods=['GET', 'POST'])
def update():
	msg = ''
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM Accounts WHERE Empid = % s',(session['Empid'], ))
	account = cursor.fetchone()
	if 'loggedin' in session:
		if request.method == 'POST' and 'password' in request.form and 'email' in request.form :
			Empid = session['Empid']
			password = request.form['password']
			email = request.form['email']
			
			if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
				msg = 'Invalid email address !'
			else:
				cursor.execute('UPDATE accounts SET password=MD5(% s), email =% s WHERE Empid =% s', (password, email,Empid, ))
				mysql.connection.commit()
				msg = 'You have successfully updated !'
		elif request.method == 'POST':
			msg = 'Please fill out the form !'
		return render_template("update.html", msg=msg,account=account)
	return redirect(url_for('login'))

@app.route("/display")
def display():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM Accounts WHERE Empid = % s',
					(session['Empid'], ))
		account = cursor.fetchone()
		return render_template("display.html", account=account)
	return redirect(url_for('login'))



@app.route("/index")
def index():
	if 'loggedin' in session:
		return render_template("index.html")
	return redirect(url_for('login'))

@app.route("/supplier")
def supplier():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM Supplier ")
		Supplier = cursor.fetchall()
		return render_template("supplier.html",Supplier=Supplier)
	return redirect(url_for('login'))

@app.route("/addsuplform")
def addsuplform():
	if 'loggedin' in session:
		return render_template("addsupl.html")
	return redirect(url_for('login'))

@app.route("/addsupl", methods=['GET', 'POST'])
def addsupl():
    if request.method == 'POST' and 'Suplid' in request.form and 'SuplName' in request.form and 'SuplEmail' in request.form and 'SuplPh' in request.form and 'SuplAddr' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        Suplid = request.form['Suplid']
        SuplName = request.form['SuplName']
        SuplEmail = request.form['SuplEmail']
        SuplPh = request.form['SuplPh']
        SuplAddr = request.form['SuplAddr']
        # Insert into Stock table
        try:
            query = "INSERT INTO Supplier (Suplid,SuplName, SuplEmail, SuplPh, SuplAddr) VALUES (%s, %s, %s, %s, %s)"
            values = (Suplid, SuplName, SuplEmail, SuplPh,SuplAddr )
            cursor.execute(query, values)
            mysql.connection.commit()
            flash('Supplier added successfully', 'success')
            return redirect(url_for('addsuplform'))
        except Exception as e:
            flash(f"Error: {e}", 'error')
    return redirect(url_for('addsuplform'))

@app.route("/deletesupl", methods=['GET', 'POST'])
def deletesupl():
	msg = ''
	if 'loggedin' in session:
		suplid = request.args.get('suplid')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		try:
			cursor.execute("DELETE FROM Supplier WHERE Suplid = %s", (suplid,))
			mysql.connection.commit()  # Commit changes to the database
			msg='Supplier record deleted successfully'
			
		except Exception as e:
			msg='Suppler record deletion failed'
		finally:
			cursor.execute('SELECT * FROM Supplier')
			Supplier = cursor.fetchall()
			return render_template("supplier.html", Supplier=Supplier,msg=msg)
	return redirect(url_for('login'))

# @app.route("/billprint")
# def billprint():
# 	if 'loggedin' in session:
# 		return render_template("bill2.html")
# 	return redirect(url_for('login'))

@app.route('/printbill')
def printbill():
	if 'loggedin' in session:
		tranid = request.args.get('tranid')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM TDview WHERE Tranid=%s ",(tranid,))
		transactiondetails = cursor.fetchall()
		cursor.execute("SELECT * FROM PresView WHERE Tranid=%s ",(tranid,))
		pres = cursor.fetchall()
		cursor.execute('SELECT * FROM transactionview WHERE Tranid=%s',(tranid,))
		transactionview = cursor.fetchone()
		
		html_content = render_template('bill2.html', transactiondetails=transactiondetails,transactionview=transactionview,pres=pres)
    	
		options = {
			'page-size': 'A4',
			'margin-top': '25.4mm',
			'margin-right': '25.4mm',
			'margin-bottom': '25.4mm',
			'margin-left': '31.75mm',
		}

		pdfkit.from_string(html_content, 'bill2.pdf', options=options)

		with open('output.pdf', 'rb') as pdf_file:
			response = make_response(pdf_file.read())
			response.headers['Content-Type'] = 'application/pdf'
			response.headers['Content-Disposition'] = 'attachment; filename=bill'+tranid+'.pdf'
		return response
	return redirect(url_for('login'))

@app.route("/transactionview")
def transactionview():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM transactionview')
		transactionview = cursor.fetchall()
		return render_template("transactions.html", transactionview=transactionview)
	return redirect(url_for('login'))

@app.route("/viewbill", methods=['GET', 'POST'])
def viewbill():
	if 'loggedin' in session:
		tranid = request.args.get('tranid')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM TDview WHERE Tranid=%s ",(tranid,))
		transactiondetails = cursor.fetchall()
		cursor.execute("SELECT * FROM PresView WHERE Tranid=%s ",(tranid,))
		prescriptionview = cursor.fetchall()
		cursor.execute('SELECT * FROM transactionview WHERE Tranid=%s',(tranid,))
		transactionview = cursor.fetchone()
		return render_template("customerbill.html", transactiondetails=transactiondetails,transactionview=transactionview,prescriptionview=prescriptionview)
	return redirect(url_for('login'))

@app.route("/display_med")
def display_med():
	msg=''
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM Medicine')
		medicines = cursor.fetchall()
		return render_template("display_med.html", medicines=medicines,msg=msg)
	return redirect(url_for('login'))

@app.route("/search_med", methods=['GET', 'POST'])
def search_med():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		if request.method == 'POST' and 'MedName' in request.form :
			MedName = request.form['MedName']
			if MedName=='NULL':
				query = "SELECT * FROM Medicine"
				found_meds = cursor.fetchall()
			else:
				query = "SELECT * FROM Medicine WHERE MedName LIKE %s"
				cursor.execute(query, (MedName + '%',))			
				found_meds = cursor.fetchall()
			return render_template("display_med.html", found_meds=found_meds)
	return redirect(url_for('login'))

@app.route("/addmedform")
def addmedform():
	if 'loggedin' in session:
		return render_template("addmed.html")
	return redirect(url_for('login'))



@app.route("/deletemed", methods=['GET', 'POST'])
def deletemed():
	msg = ''
	if 'loggedin' in session:
		medid = request.args.get('medid')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		try:
			cursor.execute("DELETE FROM Medicine WHERE Medid = %s", (medid,))
			mysql.connection.commit()  # Commit changes to the database
			msg='Medicine record deleted successfully'
			
		except Exception as e:
			msg='Stock record deletion failed'
		finally:
			cursor.execute('SELECT * FROM Medicine')
			medicines = cursor.fetchall()
			return render_template("display_med.html", medicines=medicines,msg=msg)
	return redirect(url_for('login'))

@app.route("/addmed", methods=['GET', 'POST'])
def addmed():
    if request.method == 'POST' and 'MedName' in request.form and 'MedDesc' in request.form and 'MedQty' in request.form and 'MedPrice' in request.form and 'PresReq' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        MedName = request.form['MedName']
        MedDesc = request.form['MedDesc']
        MedQty = request.form['MedQty']
        MedPrice = float(request.form['MedPrice'])
        PresReq = int(request.form['PresReq'])
        # Insert into Stock table
        try:
            query = "INSERT INTO Medicine (MedName,MedDesc, MedQty, MedPrice, PresReq) VALUES (%s, %s, %s, %s, %s)"
            values = (MedName, MedDesc, MedQty, MedPrice,PresReq )
            cursor.execute(query, values)
            mysql.connection.commit()
            flash('Medicine added successfully', 'success')
            return redirect(url_for('addmedform'))
        except Exception as e:
            flash(f"Error: {e}", 'error')
    return redirect(url_for('addstockform'))

@app.route("/updatemedform")
def updatemedform():
	if 'loggedin' in session:
		medid = request.args.get('medid')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM Medicine WHERE Medid=%s',(medid,))
		med = cursor.fetchone()
		return render_template("updatemed.html",med=med)
	return redirect(url_for('login'))

@app.route("/updatemed", methods=['GET', 'POST'])
def updatemed():
	msg = ''
	if 'loggedin' in session:
		medid = request.args.get('medid')
		if request.method == 'POST' and 'MedName' in request.form and 'MedDesc' in request.form and 'MedQty' in request.form and 'MedPrice' in request.form and 'PresReq' in request.form:
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			MedName = request.form['MedName']
			MedDesc = request.form['MedDesc']
			MedQty = request.form['MedQty']
			MedPrice = float(request.form['MedPrice'])
			PresReq = int(request.form['PresReq'])
			# Insert into Stock table
			try:
				query = "UPDATE Medicine SET MedName=%s,MedDesc=%s,MedQty=%s, MedPrice=%s,PresReq=%s WHERE Medid=%s"
				values = (MedName, MedDesc, MedQty, MedPrice,PresReq,medid )
				cursor.execute(query, values)
				mysql.connection.commit()
				flash('Medicine updated successfully', 'success')
				return redirect(url_for('display_med'))
			except Exception as e:
				flash(f"Error: {e}", 'error')
		return redirect(url_for('display_med'))
	return redirect(url_for('login'))


@app.route("/stock")
def stock():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM stockview')
        stockview = cursor.fetchall()

        cursor.execute('SELECT Stockid FROM Medicine JOIN Stock ON Medicine.Medid = Stock.Medid WHERE (StockExpYear = YEAR(CURDATE()));')
        expiredstock = cursor.fetchall()
        expiredstock_ids = [row['Stockid'] for row in expiredstock]

        if expiredstock:
            msg = 'There are expired stocks or stocks which are about to expire. Remove them ASAP'

        return render_template("stock.html", stockview=stockview, expiredstock_ids=expiredstock_ids, msg=msg)
    return redirect(url_for('login'))


@app.route("/addstockform")
def addstockform():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT Medid,MedName FROM Medicine')
		medlist = cursor.fetchall()
		cursor.execute('SELECT Suplid,SuplName FROM Supplier')
		suplist = cursor.fetchall()
		return render_template("addstock.html",medlist=medlist,suplist=suplist)
	return redirect(url_for('login'))

@app.route("/addstock", methods=['GET', 'POST'])
def addstock():
    if request.method == 'POST' and 'Medid' in request.form and 'Suplid' in request.form and 'StockQty' in request.form and 'StockExpYear' in request.form and 'StockExpMonth' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        medid = int(request.form['Medid'])
        suplid = request.form['Suplid']
        stock_qty = int(request.form['StockQty'])
        exp_year = int(request.form['StockExpYear'])
        exp_month = int(request.form['StockExpMonth'])
        # Insert into Stock table
        try:
            query = "INSERT INTO Stock (Medid, Suplid, StockQty, StockExpYear, StockExpMonth) VALUES (%s, %s, %s, %s, %s)"
            values = (medid, suplid, stock_qty, exp_year, exp_month)
            cursor.execute(query, values)
            mysql.connection.commit()
            flash('Stock added successfully', 'success')
            return redirect(url_for('addstockform'))
        except Exception as e:
            flash(f"Error: {e}", 'error')
    return redirect(url_for('addstockform'))


@app.route("/deletestock", methods=['GET', 'POST'])
def deletestock():
	msg = ''
	if 'loggedin' in session:
		stockid = request.args.get('stockid')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		try:
			cursor.execute("DELETE FROM Stock WHERE Stockid = %s", (stockid,))
			mysql.connection.commit()  # Commit changes to the database
			msg='Stock record deleted successfully'
			
		except Exception as e:
			msg='Stock record deletion failed'
		finally:
			cursor.execute('SELECT * FROM stockview')
			stockview = cursor.fetchall()
			return render_template("stock.html", stockview=stockview,msg=msg)
	return redirect(url_for('login'))

@app.route("/billingform")
def billingform():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT Empid FROM Employee WHERE EmpRole="BI"')
		Emp = cursor.fetchall()
		return render_template("billingform.html",Emp=Emp)
	return redirect(url_for('login'))

@app.route("/tdform", methods=['GET', 'POST'])
def tdform():
	if request.method == 'POST' and 'CustName' in request.form and 'CustGender' in request.form and 'CustPh' in request.form and 'TranDate' in request.form and 'Empid' in request.form:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		CustName = request.form['CustName']
		CustGender = request.form['CustGender']
		CustPh = request.form['CustPh']
		TranDate = request.form['TranDate']
		Empid = request.form['Empid']
		try:
			query = "CALL InsertCustomerAndTransaction (%s, %s, %s, %s, %s)"
			values = (CustName, CustGender, CustPh, TranDate,Empid, )
			cursor.execute(query, values)
			mysql.connection.commit()
			flash('Transaction and Customer details added successfully', 'success')
		except Exception as e:
			flash(f"Error: {e}", 'error')
		cursor.execute("SELECT MAX(Tranid) AS tranid FROM Transaction")
		t=cursor.fetchone()
		tranid=t.get('tranid')
		cursor.execute('SELECT Medid,MedName,PresReq FROM Medicine')
		medlist = cursor.fetchall()
		return render_template("tdform.html",tranid=tranid,medlist=medlist) #issueee rendering tdform agn
	return redirect(url_for('billingform.html'))

		

@app.route("/checkmed", methods=['GET', 'POST'])
def checkmed():
	if request.method == 'POST' and 'Medid' in request.form and 'Medunits' in request.form:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		tranid = request.args.get('tranid')
		Medid = int(request.form['Medid'])
		Medunits = int(request.form['Medunits'])
		cursor.execute('SELECT PresReq FROM Medicine WHERE Medid=%s',(Medid,))
		p= cursor.fetchone()
		pres=p.get('PresReq')
		return render_template("tdformnext.html",tranid=tranid,pres=pres,medid=Medid,medunits=Medunits)
	return redirect(url_for('tdform'))

@app.route("/inserttdpres", methods=['GET', 'POST'])
def inserttdpres():
	if request.method == 'POST' and 'tranid' in request.form and 'medid' in request.form and 'medunits' in request.form and 'DocName' in request.form and 'Dosage' in request.form:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		tranid = int(request.form['tranid'])
		medid = int(request.form['medid'])
		medunits = int(request.form['medunits'])
		DocName = request.form['DocName']
		Dosage = request.form['Dosage']
		try:
			query = "CALL InsertTransactionDetailsAndPrescription (%s, %s, %s, %s, %s)"
			values = (tranid, medid, medunits, DocName,Dosage )
			cursor.execute(query, values)
			mysql.connection.commit()
			flash('Transactiondetails and Prescription details added successfully', 'success')
			cursor.execute('SELECT Medid,MedName,PresReq FROM Medicine')
			medlist = cursor.fetchall()
			return render_template("tdform.html",tranid=tranid,medlist=medlist)
		except Exception as e:
			flash(f"Error: {e}", 'error')
	return redirect(url_for('billingform'))

# @app.route("/inserttd", methods=['GET', 'POST'])
# def inserttd():
# 	if request.method == 'POST' and 'tranid' in request.form and 'medid' in request.form and 'medunits' in request.form and 'prescid' in request.form:
# 		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
# 		tranid = request.args.get('tranid')
# 		medid = request.args.get('medid')
# 		medunits = request.args.get('medunits')
# 		try:
# 			query = "INSERT INTO TransactionDetails(Tranid,Medid,Medunits,Prescid) VALUES(%s, %s, %s, NULL)"
# 			values = (tranid, medid, medunits,)
# 			cursor.execute(query, values)
# 			mysql.connection.commit()
# 			flash('Transactiondetails record added successfully', 'success')
# 			cursor.execute('SELECT Medid,MedName,PresReq FROM Medicine')
# 			medlist = cursor.fetchall()
# 			return render_template("tdform.html",tranid=tranid,medlist=medlist)
# 		except Exception as e:
# 			flash(f"Error: {e}", 'error')
# 	return redirect(url_for('billingform'))

@app.route("/inserttd", methods=['POST'])
def inserttd():
    if request.method == 'POST' and 'tranid' in request.form and 'medid' in request.form and 'medunits' in request.form and 'prescid' in request.form:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        tranid = int(request.form['tranid'])
        medid = int(request.form['medid'])
        medunits = int(request.form['medunits'])
        #prescid = request.form['prescid']  # Update this variable name

        try:
            query = "INSERT INTO TransactionDetails(Tranid, Medid, Medunits, Prescid) VALUES(%s, %s, %s,NULL)"
            values = (tranid, medid, medunits,)
            cursor.execute(query, values)
            mysql.connection.commit()
            flash('Transactiondetails record added successfully', 'success')
            cursor.execute('SELECT Medid, MedName, PresReq FROM Medicine')
            medlist = cursor.fetchall()
            return render_template("tdform.html", tranid=tranid, medlist=medlist)
        except Exception as e:
            flash(f"Error: {e}", 'error')
    return redirect(url_for('billingform'))



if __name__ == "__main__":
	app.run(host="localhost", port=int("5000"))
