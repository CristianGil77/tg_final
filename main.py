from flask import Flask, request, make_response, render_template, redirect, session, url_for, flash, Response
from app import create_app
from app.forms import CommonForm
from app.yaml import WriteYaml
from app.NodesCaller import RosCaller
import subprocess
import signal
import os

import logging
logging.basicConfig(level=logging.DEBUG)

app = create_app()
app.system_status = "Stopped"
yaml = WriteYaml()
app.myRoscaller = RosCaller()
process = None

#print(yaml.path)


@app.route('/')
def index():
    """Index method to redirect to home page

    Returns:
        server response: redirect to /home route 
    """
    user_ip = request.remote_addr
    response = make_response(redirect('/home'))
    session['user_ip'] = user_ip
    return response


@app.route('/home', methods=['GET', 'POST'])
def home():
    """Home method - welcome page

    Returns:
        server response: Home-page for platform welcome
    """
    context = {
        'module': 'home',
        'form_name': 'Welcome!',
        'system_status': app.system_status,
    }

    if request.method=='POST':
        context['system_status'] = app.system_status


    return render_template('home.html', **context)


@app.route('/system', methods=['POST'])
def system():
    """Systems control method

    Returns:
        context: Alert context to frontend modals
    """    
    system_request = request.form.to_dict()
    user_exec = system_request['system']
    global process

    if(user_exec == 'Start'):
        #logging.info("HEY1")
        
        fileName = "config/common/common.yaml"
        bool_acces, opcion = yaml.yaml_to_dict(fileName, ('use_detection'))
        print("opcion", opcion)

        if bool_acces:
            if opcion:
                app.opcion_jk = 1
            else:
                app.opcion_jk = 2
        else:
            pass

        app.system_status = 'Running'

        print("cargando el modelo rna")
        script_path = "app/tg_app/app.py"
        #subprocess.run(["python3", script_path])
       
        if process is None:
            # Ruta al script Python que deseas ejecutar
            #script_path = "/ruta/a/tu_script.py"
            process = subprocess.Popen(["python3", script_path])


    elif (user_exec == 'PowerOff'):
        app.myRoscaller.stop()
        #logging.info("HEY apagar!")
        app.system_status = 'Stopped'
        app.myRoscaller.shutdownall()

    else:
        if process is not None:
            os.kill(process.pid, signal.SIGTERM)
            process = None
        app.system_status = 'Stopped'
        


    #logging.info("##Status_system --> "+user_exec) 



    return ({'result': True, 'info': 'Systems response to '+user_exec+' command'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug= True)
