from flask import Flask,render_template, request, redirect,url_for, make_response,send_file, session
import sqlite3
from flask_cors import CORS
import pdfkit
import io
import platform
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'

port = int(os.environ.get("PORT", 5000))


#connection to db
def db_connection():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    return con


if platform.system() == 'Windows':
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
else:
    path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'


config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)


#config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')



#get all data
@app.route('/getdata',methods=['GET'])
def get_data():
    con = db_connection()
    cur = con.cursor()
    cur.execute("select * from info")
    data = cur.fetchall()
    return render_template("certificate.html",datas=data)
    
    #return jsonify([dict(d) for d in details])



#certificate data
@app.route('/', methods=['POST', 'GET'])
def certi():
    if request.method == 'POST':
        gname = request.form['gname']
        bname = request.form['bname']
        place = request.form['place']
        mrg_date = request.form['mrg_date']

    
        try:
            con = db_connection()
            con.execute("INSERT INTO info (gname, bname, place, mrg_date) VALUES (?, ?, ?, ?)",
                        (gname, bname, place, mrg_date))
            con.commit()
            con.close()
            return redirect(url_for('get_data'))
        except sqlite3.IntegrityError:
            return "Failed to insert data."
    return render_template("input.html")
   


@app.route('/display', methods=['POST','GET'])
def display():
     return render_template("certificate1.html")


#fetch single data for Template-1
@app.route('/temp1/<int:id>',methods=['GET'])
def temp1(id):
    con = db_connection()
    cur = con.cursor()
    cur.execute("select * from info where id = ?",(id,))
    data = cur.fetchone()
    return render_template("certificate1.html",user=data)



#Template -2
@app.route('/temp2/<int:id>',methods=['GET'])
def temp2(id):
     con = db_connection()
     cur = con.cursor()
     cur.execute("select * from info where id = ?",(id,))
     data = cur.fetchone()
     return render_template("certificate2.html",user=data)



#Template -3
@app.route('/temp3/<int:id>',methods=['GET'])
def temp3(id):
    con = db_connection()
    cur = con.cursor()
    cur.execute("select * from info where id = ?",(id,))
    data = cur.fetchone()
    con.close()

    return  render_template("certificate3.html", user=data)
    



#Edit the templates
# @app.route('/edit/<string:id>', methods=['POST','GET'])
# def edit(id):
#     if request.method == 'POST':
#         gname = request.form['gname']
#         bname = request.form['bname']
#         place = request.form['place']
#         mrg_date = request.form['mrg_date']
#         con = db_connection()
#         cur = con.cursor()
#         cur.execute("update info set gname = ? , bname = ? where id =? ", (gname,bname,id))
#         con.commit()
#         return redirect(url_for("get_data"))
#     con = db_connection()
#     cur = con.cursor()
#     cur.execute("select * from info where id = ?", (id,))
#     data = cur.fetchone() 
#     result = {
#             "gname": gname,
#             "bname": bname,
#             "place": place,
#             "mrg_date": mrg_date
#         }
#     session['certi_result'] = result
#     print(result)
#     return render_template("edit.html", data=data, result=result)




@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):
    con = db_connection()
    cur = con.cursor()
    
    if request.method == 'POST':
        gname = request.form['gname']
        bname = request.form['bname']
        place = request.form['place']
        mrg_date = request.form['mrg_date']

        cur.execute("UPDATE info SET gname = ?, bname = ?, place = ?, mrg_date = ? WHERE id = ?", 
                    (gname, bname, place, mrg_date, id))
        con.commit()

        #Save updated result in session
        session['certi_result'] = {
            "gname": gname,
            "bname": bname,
            "place": place,
            "mrg_date": mrg_date
        }
        session['certi_id'] = id  # Track ID in session

        return redirect(url_for("get_data"))

    cur.execute("SELECT * FROM info WHERE id = ?", (id,))
    data = cur.fetchone()

    result = {
        "gname": data[1],
        "bname": data[2],
        "place": data[3],
        "mrg_date": data[4]
    }

    session['certi_result'] = result
    session['certi_id'] = id  # Track ID in session
    
    return render_template("edit.html", data=data,result=result)




#delete
@app.route('/delete/<string:id>' , methods = ['GET'])
def delete(id):
    con = db_connection()
    cur = con.cursor()
    cur.execute("delete from info where id=? ",(id,))
    con.commit()
    return redirect(url_for("get_data"))




#pdf download temp_3
@app.route('/download_pdf_temp3/<string:iid>')
def download_pdf_temp3(iid):
    result = session.get('certi_result')
    certi_id = session['certi_id']
    # print(result)
    # print("hello")
    # print(certi_id)
    # print(iid)
    
     # If certi_result not in session, fallback to fetching from DB
    if not result or iid != certi_id:
        con = db_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM info WHERE id = ?", (iid,))
        data = cur.fetchone()
        if not data:
            return "No data found for certificate.", 404

        result = {
            "gname": data[1],
            "bname": data[2],
            "place": data[3],
            "mrg_date": data[4]
        }

    if not result:
        return "No certificate data found. Please submit the form first.", 400

    options = { 'enable-local-file-access': '',
               'page-size': 'A4',
                'encoding': 'UTF-8',}
     
    html = render_template('certificate3.html', user=result,options=options)
    pdf = pdfkit.from_string(html, False, configuration=config)

    return send_file(io.BytesIO(pdf),
                     as_attachment=True,
                     download_name="marriage_certificate.pdf",
                     mimetype='application/pdf')






#pdf download temp_2
@app.route('/download_pdf_temp2/<string:iid>')
def download_pdf_temp2(iid):
    result = session.get('certi_result')
    certi_id = session['certi_id']
    
     # If certi_result not in session, fallback to fetching from DB
    if not result or iid != certi_id:
        con = db_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM info WHERE id = ?", (iid,))
        data = cur.fetchone()
        if not data:
            return "No data found for certificate.", 404

        result = {
            "gname": data[1],
            "bname": data[2],
            "place": data[3],
            "mrg_date": data[4]
        }

    if not result:
        return "No data found.", 400

    html = render_template('certificate2.html', user=result)
    options = {'enable-local-file-access': ''}
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)

    return send_file(
        io.BytesIO(pdf),
        as_attachment=True,
        download_name='marriage_certificate.pdf',
        mimetype='application/pdf'
    )


#pdf download temp_1
@app.route('/download_pdf_temp1/<string:iid>')
def download_pdf_temp1(iid):
    result = session.get('certi_result')
    certi_id = session['certi_id']
    # print(result)
    # print("hello")
    # print(certi_id)
    # print(iid)
    
     # If certi_result not in session, fallback to fetching from DB
    if not result or iid != certi_id:
        con = db_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM info WHERE id = ?", (iid,))
        data = cur.fetchone()
        if not data:
            return "No data found for certificate.", 404

        result = {
            "gname": data[1],
            "bname": data[2],
            "place": data[3],
            "mrg_date": data[4]
        }

    if not result:
        return "No data found.", 400

    html = render_template('certificate1.html', user=result)
    options = {'enable-local-file-access': ''}
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)

    return send_file(
        io.BytesIO(pdf),
        as_attachment=True,
        download_name='marriage_certificate.pdf',
        mimetype='application/pdf'
    )




app.run(host="0.0.0.0", port=port)
#app.run(debug=True)

