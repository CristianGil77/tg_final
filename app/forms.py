from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, BooleanField, DecimalField, HiddenField
from wtforms.validators import DataRequired, EqualTo, InputRequired, Regexp, Length, Optional, Email, NumberRange, AnyOf

from app.yaml import WriteYaml

class CommonForm(FlaskForm):
    """Form general params

    Args:
        FlaskForm (WTF form): Parent class of wtf form for render content
    """    

    miyaml = WriteYaml()

    #common
    fileName = "config/common/common.yaml"
    bool_common, dict_common = miyaml.yaml_to_dict_general(fileName, parents=False)

    if not bool_common:
        dict_common["user_height"] = 1.7
        dict_common["maximum_pcl_obstacles"] = 3
        dict_common["detection_msg_period"] = 0.5
        dict_common["use_detection"] = True
        dict_common["use_planning"] = False
        dict_common["steps"] = 0.5
        dict_common["audio_speed"] = 2
        dict_common["audio_lenght"] = 2
        dict_common["audio_language"] = 1
        dict_common["bluetooth_addres"] = "00:42:79:3F:D8:8F"
        dict_common["use_steps"] = True
        dict_common["use_imu"] = False
        dict_common["send_pasos"] = False
        dict_common["feedback_mode"] = 3


    print(dict_common)

    user_height = DecimalField(
        'User height', places=1,
        validators=[InputRequired(), NumberRange(min=0.5, max=2.5)], 
        default=dict_common["user_height"], description="Meters"
        )

        
    steps = DecimalField(
        'Steps Length', places=1,
        validators=[InputRequired(), NumberRange(min=0.15, max=0.8)], 
        default=dict_common["steps"], description="Length in meters"
        )  # Maximum number of "detected" obstacles in the PointCloud to describe to the user
    

    audio_speed = DecimalField(
        'Audio Speed', places=1,
        validators=[InputRequired(), NumberRange(min=0.5, max=2.5)],
        default=dict_common["audio_speed"], description="1: slow, 2: fast")  # Time in seconds (NO ESTA SIENDO USADO AUN)
    
    feedback_mode = DecimalField(
        'Feedback mode', places=1,
        validators=[InputRequired(), AnyOf(values=[1,2,3,4])],
        default=dict_common["feedback_mode"], description="1: class+orientation+distance, 2: class+distance+beep, 3: class+bepp*volumen, 4: class+ Nbeep")  # Time in seconds (NO ESTA SIENDO USADO AUN)
    


    
    # audio_language = DecimalField(
    #     'Audio language', places=1,
    #     validators=[InputRequired(), AnyOf(values=[0,1,2,3])],
    #     default=dict_common["audio_language"], description="0: English, 1: Spanish, 2: French, 3: German ")  # Time in seconds (NO ESTA SIENDO USADO AUN)
    
    bluetooth_addres = StringField(
        'bluetooth addres', validators=[InputRequired()], default=dict_common["bluetooth_addres"])
    

    use_imu = BooleanField(
        'Use Imu', validators=[Optional()], default=dict_common["use_imu"]) 
    
    submit = SubmitField('Update')  # Submit Button

class PlannerForm(FlaskForm):
    """Form Local Planner params

    Args:
        FlaskForm (WTF form): Parent class of wtf form for render content
    """   

    miyaml = WriteYaml()

    #common
    fileName = "config/local_planner/params.yaml"
    bool_, dict_ = miyaml.yaml_to_dict_general(fileName, parents=False)

    if not bool_:
        dict_["Maximun_distance"] = 3.0
    
    Maximun_distance = DecimalField(
        'Maximum distance', places=1,
        validators=[InputRequired(), NumberRange(min=2.5, max=10)],
        default=float(dict_["Maximun_distance"]), description="Distance in meters to search free space and calculate paths.")
    current_form = HiddenField('current_form', render_kw={"value": "planner_form"})
    submit = SubmitField('Update')  # Submit Button

class YoloForm(FlaskForm):
    """Form Yolo V5 params

    Args:
        FlaskForm (WTF form): Parent class of wtf form for render content
    """   

    miyaml = WriteYaml()

    #common
    fileName = "config/yolov5/yolov5_params.yaml"
    bool_, dict_ = miyaml.yaml_to_dict_general(fileName, parents=False)

    if not bool_:
        dict_["confidence_threshold"] = 0.25
        dict_["weights"] = "Yolov5_S_Freeze_subir4_pto_simpl_half.engine"
        dict_["data"] = 'data.yaml'
        dict_["iou_threshold"] = 0.45
        dict_["topk"] = 10
        dict_["inference_size_"] = 416
        #dict_["input_image_topic"] = '/zedm/zed_node/left/image_rect_color'
    
    weights = StringField(
        'Weights', validators=[InputRequired()], 
        default=dict_["weights"])

    # data = StringField(
    #     'data',  validators=[InputRequired()], 
    #     default=dict_["data"])
    
    confidence_threshold = DecimalField(
        'Confidence threshold', places=2,
        validators=[InputRequired(), NumberRange(min=0.1, max=1)],
        default=float(dict_["confidence_threshold"]))
    
    iou_threshold = DecimalField(
        'Iou threshold', places=2,
        validators=[InputRequired(), NumberRange(min=0.1, max=1)],
        default=float(dict_["iou_threshold"]))

    inference_size_ = DecimalField(
        'Inference size', places=0,
        validators=[InputRequired(), NumberRange(min=100, max=1000)],
        default=float(dict_["inference_size_"]))
    
    topk = DecimalField(
        'Topk', places=1,
        validators=[InputRequired(), NumberRange(min=5, max=200)],
        default=int(dict_["topk"]))

    # input_image_topic = StringField(
    #     'Input image topic', validators=[InputRequired()], 
    #     default=dict_["input_image_topic"])
    
    current_form = HiddenField('current_form', render_kw={
                               "value": "yolo_form"})
    submit = SubmitField('Update')  # Submit Button

class PreprocessForm_general(FlaskForm):
    """Form Preprocess general params

    Args:
        FlaskForm (WTF form): Parent class of wtf form for render content
    """
    miyaml = WriteYaml()

    #common
    fileName = "config/preprocess_node/preprocess_params.yaml"
    bool_, dict_ = miyaml.yaml_to_dict_general(fileName, parents=False)

    if not bool_:
        dict_["use_blur_filter"] = True
        dict_["use_hist_equ"] = False
        dict_["use_clahe"] = False
        dict_["blur_threshold"] = 100
        dict_["clahe_clip_limit"] = 2.0
        dict_["clahe_tile_grid_size"] = 8
        dict_["max_angle"] = 20
        
    use_hist_equ = BooleanField(
        'Global histogram',  validators=[Optional()], default=dict_["use_hist_equ"])
    use_blur_filter = BooleanField(
        'Blur filter',  validators=[Optional()], default=dict_["use_blur_filter"])
    use_clahe = BooleanField(
        'CLAHE',  validators=[Optional()], default=dict_["use_clahe"])


    blur_threshold = DecimalField(
        'Blur threshold', places=1,
        validators=[InputRequired(), NumberRange(min=0, max=1000)],
        default=int(dict_["blur_threshold"]), description= "Minimum Laplacian variance for blur detection.")

    clahe_clip_limit = DecimalField(
        'Clahe clip limit', places=1,
        validators=[InputRequired(), NumberRange(min=0, max=10)],
        default=float(dict_["clahe_clip_limit"]), description= "Maximum contrast limit in a region.")
    
    clahe_tile_grid_size = DecimalField(
        'Clahe tile grid size', places=1,
        validators=[InputRequired(), NumberRange(min=0, max=10)],
        default=int(dict_["clahe_tile_grid_size"]), description= "Size of subregions for local equalization.")
    
    max_angle = DecimalField(
        'Angle threshold', places=0,
        validators=[InputRequired(), NumberRange(min=15, max=90)],
        default=float(dict_["max_angle"]), description="The front is defined from -angle threshold to +angle threshold.")
    
    

    

    current_form = HiddenField('current_form', render_kw={
                               "value": "preprocess_form"})
    general = SubmitField('Update')  # Submit Button



class IsaacForm_general(FlaskForm):
    """Form Isaac general params

    Args:
        FlaskForm (WTF form): Parent class of wtf form for render content
    """
    miyaml = WriteYaml()

    #common
    fileName = "config/isaac/isaac_params.yaml"
    bool_, dict_ = miyaml.yaml_to_dict_general(fileName, parents=True)

    if not bool_:
        dict_["left_image_topic"] = "/zedm/zed_node/left/image_rect_color"
        dict_["left_camera_info_topic"] = "/zedm/zed_node/left/camera_info"
        dict_["right_image_topic"] = "/zedm/zed_node/right/image_rect_color"
        dict_["right_camera_info_topic"] = "/zedm/zed_node/right/camera_info"

    left_image_topic = StringField(
        'left_image_topic', validators=[InputRequired()], 
        default=dict_["left_image_topic"], description="ROS topic string.")
            
    left_camera_info_topic = StringField(
        'left_camera_info_topic', validators=[InputRequired()], 
        default=dict_["left_camera_info_topic"], description="ROS topic string.")

    right_image_topic = StringField(
        'right_image_topic', validators=[InputRequired()], 
        default=dict_["right_image_topic"], description="ROS topic string.")

    right_camera_info_topic = StringField(
        'right_camera_info_topic', validators=[InputRequired()], 
        default=dict_["right_camera_info_topic"], description="ROS topic string.")

    current_form = HiddenField('current_form', render_kw={
                               "value": "isaac_form"})
    general = SubmitField('Update')  # Submit Button


class IsaacForm_disparity(FlaskForm):
    """Form Preprocess Issac disparity filter params

    Args:
        FlaskForm (WTF form): Parent class of wtf form for render content
    """
    miyaml = WriteYaml()

    #common
    fileName = "config/isaac/isaac_params.yaml"
    bool_, dict_ = miyaml.yaml_to_dict_general(fileName, parents=True)

    if not bool_:
        dict_["backends"] = "CUDA"
        dict_["max_disparity"] = 64
        dict_["min_perc"] = 0.2
        
    backends  = StringField(
        'Backends', validators=[InputRequired(), AnyOf(values=['CUDA', 'XAVIER', 'ORIN'])], 
        default=dict_["backends"], description="The VPI backend to use, which is CUDA by default (options: 'CUDA', 'XAVIER', 'ORIN').")
    
    max_disparity = DecimalField(
        'Maximum disparity', places=0,
        validators=[InputRequired(), NumberRange(min=32, max=256)],
        default=float(dict_["max_disparity"]), description="The maximum value for disparity per pixel, which is 64 by default. With ORIN backend, this value must be 128 or 256.")
    
    min_perc = DecimalField(
        'Minimum Percentage', places=1,
        validators=[InputRequired(), NumberRange(min=0.1, max=0.5)],
        default=float(dict_["min_perc"]), description="The percentage used in the histogram to search obstacles (1.0 is the maximum points the obstacles).")
    
    current_form = HiddenField('current_form', render_kw={
                               "value": "isaac_form"})
    disparity = SubmitField('Update')  # Submit Button


class IsaacForm_pointclouds(FlaskForm):
    """Form Preprocess Issac disparity filter params

    Args:
        FlaskForm (WTF form): Parent class of wtf form for render content
    """
    miyaml = WriteYaml()

    #common
    fileName = "config/isaac/isaac_params.yaml"
    bool_, dict_ = miyaml.yaml_to_dict_general(fileName, parents=True)

    if not bool_:
        dict_["use_color"] = False

    use_color = BooleanField(
        'Use color', validators=[Optional()], default=dict_["use_color"])
    current_form = HiddenField('current_form', render_kw={
                               "value": "isaac_form"})
    pointclouds = SubmitField('Update')


class ZedcommonForm(FlaskForm):
    """Form Zed common params

    Args:
        FlaskForm (WTF form): Parent class of wtf form for render content
    """
    miyaml = WriteYaml()

    #common
    fileName = "config/zed_wrapper/common.yaml"
    bool_, dict_ = miyaml.yaml_to_dict_general(fileName, parents=False)
    
    if not bool_:
        dict_["resolution"] = 3
        dict_["quality"] = 3
        dict_["sensing_mode"] = 1


    resolution = DecimalField(
        'Resolution', places=0,
        validators=[InputRequired(), AnyOf(values=[0,1,2,3])],
        default=float(dict_["resolution"]), description="# '0': HD2K, '1': HD1080, '2': HD720, '3': VGA")
    
    quality = DecimalField(
        'Quality', places=0,
        validators=[InputRequired(), AnyOf(values=[0,1,2,3,4])],
        default=float(dict_["quality"]), description="# '0': NONE, '1': PERFORMANCE, '2': QUALITY, '3': ULTRA - '4': NEURAL ")
    
    sensing_mode = DecimalField(
        'Sensing mode', places=0,
        validators=[InputRequired(), AnyOf(values=[0,1])],
        default=float(dict_["sensing_mode"]), description="# '0': STANDARD, '1': FILL")
    
        
    
    current_form = HiddenField('current_form', render_kw={
                               "value": "zedcommon_form"})
    submit = SubmitField('Update')  # Submit Button