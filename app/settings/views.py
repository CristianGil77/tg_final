from flask import render_template, redirect, request,flash, url_for, session, current_app as app
from . import settings
from ..forms import CommonForm
from ..yaml import WriteYaml

yaml = WriteYaml()

@settings.route('/', methods=['GET', 'POST'])
def setting():
    """Setting method - Basic configuration page

    Returns:
        server response: Setting-page for platform
    """
    settings_form = CommonForm()
    context = {
        'module': 'settings.setting',
        'form_name': 'Basic parameters',
        'form_to_render': settings_form,
    }

    if settings_form.validate_on_submit():
        #file_name = 'config/common/common.yaml'
        file_name = 'config/common/common.yaml'
        file_name2 = '/home/gelbert2/audio_ws/src/audio_pkg/config/common.yaml'

        
        data = request.form.to_dict()
        del data['csrf_token']
        del data['submit']
            
        if "use_imu" not in data:
            data['use_imu'] = "false"
        
        
        success, msg = yaml.dict_to_yaml(file_name, data)
        print("hola3")
        context = {
            'module': 'settings.setting',
            'form_name': 'Basic parameters',
            'form_to_render': settings_form,
        }
        context['success'] = success
        context['success_text'] = msg
    return render_template('settings.html', **context)
