import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

import eco_hectare as eh

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jajaja'

eh_db = eh.db.DataBase(db_file='../main.db', create=False)

@app.route('/')
def index():

    return render_template('index.html')


@app.route('/devices')
def devices():

    devices = eh_db.get_devices()

    return render_template('devices.html', devices=devices)


@app.route('/devices/new', methods=('GET', 'POST'))
def device_new():

    sectors = eh_db.get_sectors()

    if request.method == 'POST':
        deveui = request.form['deveui']
        sector = request.form['sector']
        dev_type = request.form['type']

        if deveui == '':
            flash('deveui necessário!')
        else:
            status = eh_db.insert_device(deveui, sector=sector, dev_type=dev_type)
            if status != 0:
                flash('deveui já cadastrado!')
                return redirect(url_for('device_new'))
            
            return redirect(url_for('devices'))

    return render_template('device_new.html', sectors=sectors)


@app.route('/devices/<string:deveui>')
def device(deveui):

    device_data = eh_db.get_device_data(deveui)

    return render_template('device.html', device_data=device_data)

@app.route('/sectors')
def sectors():

    sectors = eh_db.get_sectors()

    return render_template('sectors.html', sectors=sectors)


@app.route('/sectors/<int:sector_id>')
def sector(sector_id):

    sector_data = eh_db.get_sector_data(sector_id)
    devices = eh_db.get_devices_by_sector(sector_id)

    return render_template('sector.html', sector=sector_data, devices=devices)


@app.route('/sectors/<int:sector_id>/edit', methods=('GET', 'POST'))
def sector_edit(sector_id):

    sector_data = eh_db.get_sector_data(sector_id)

    if request.method == 'POST':
        desc = request.form['description']
        cal = request.form['cal']

        if desc == '':
            flash('Descrição necessária!')
        elif not cal:
            flash('Calibração necessária!')
        else:
            eh_db.update_sector_data(sector_id, desc, cal)
            
            return redirect(url_for('sector', sector_id=sector_id))   

    return render_template('sector_edit.html', sector=sector_data)


@app.route('/sectors/new', methods=('GET', 'POST'))
def sector_new():

    if request.method == 'POST':
        sector_id = request.form['sector_id']
        desc = request.form['description']
        cal = request.form['cal']

        if desc == '':
            flash('Descrição necessária!')
        elif not cal:
            flash('Calibração necessária!')
        elif not sector_id:
            flash('Informe um número para o setor!')
        else:
            if eh_db.insert_sector(sector_id, description=desc, cal=cal) == -1:
                flash('Setor já cadastrado!')
                return redirect(url_for('sector_new'))
            
            return redirect(url_for('sectors'))

    return render_template('sector_new.html')


@app.route('/sectors/<int:sector_id>/delete', methods=('POST',))
def sector_delete(sector_id):

    eh_db.delete_sector(sector_id)

    return redirect(url_for('sectors'))
    

if __name__ == '__main__':
   app.run(debug = True)
