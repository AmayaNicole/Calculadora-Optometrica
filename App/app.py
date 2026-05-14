from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def conectar_db():
    conn = sqlite3.connect('historial.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS retinoscopia (id INTEGER PRIMARY KEY AUTOINCREMENT, ojo TEXT, rx TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS lensometria (id INTEGER PRIMARY KEY AUTOINCREMENT, ojo TEXT, rx TEXT)')
    conn.commit()
    return conn

@app.route('/')
def inicio():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM retinoscopia ORDER BY id DESC")
    historial_ret = cursor.fetchall()
    cursor.execute("SELECT * FROM lensometria ORDER BY id DESC")
    historial_len = cursor.fetchall()
    conn.close()
    return render_template('index.html', historial_ret=historial_ret, historial_len=historial_len)

@app.route('/calcular_retinoscopia', methods=['POST'])
def calcular_retinoscopia():
    try:
        ojo = request.form['ojo']
        m1 = float(request.form['m1'].replace(',', '.'))
        m2 = float(request.form['m2'].replace(',', '.'))
        eje1, eje2 = int(request.form['eje1']), int(request.form['eje2'])
        distancia = float(request.form['distancia'].replace(',', '.'))

        # Lógica Retinoscopía: (Más Positivo - Distancia)
        mas_pos, menos_pos, eje_cil = (m1, m2, eje2) if m1 >= m2 else (m2, m1, eje1)
        esfera = mas_pos - distancia
        cilindro = menos_pos - mas_pos
        
        rx = f"{esfera:+.2f} ({cilindro:+.2f}) x {eje_cil}°"
        conn = conectar_db(); cursor = conn.cursor()
        cursor.execute("INSERT INTO retinoscopia (ojo, rx) VALUES (?, ?)", (ojo, rx))
        conn.commit(); conn.close()
    except: pass
    return redirect(url_for('inicio'))

@app.route('/calcular_lensometria', methods=['POST'])
def calcular_lensometria():
    try:
        ojo = request.form['ojo_len']
        l1 = float(request.form['l1'].replace(',', '.'))
        eje_l1 = int(request.form['eje_l1'])
        l2 = float(request.form['l2'].replace(',', '.'))
        eje_l2 = int(request.form['eje_l2'])

        # Lógica Lensometría: Esfera = Más Positivo (SIN DISTANCIA)
        mas_pos, menos_pos, eje_cil = (l1, l2, eje_l2) if l1 >= l2 else (l2, l1, eje_l1)
        esfera = mas_pos
        cilindro = menos_pos - mas_pos
        
        rx = f"{esfera:+.2f} ({cilindro:+.2f}) x {eje_cil}°"
        conn = conectar_db(); cursor = conn.cursor()
        cursor.execute("INSERT INTO lensometria (ojo, rx) VALUES (?, ?)", (ojo, rx))
        conn.commit(); conn.close()
    except: pass
    return redirect(url_for('inicio'))

@app.route('/limpiar/<tipo>')
def limpiar(tipo):
    conn = conectar_db(); cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {tipo}")
    conn.commit(); conn.close()
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)