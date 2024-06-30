from operator import le
import ruamel.yaml
import pathlib
import shutil

from ruamel.yaml.scalarfloat import ScalarFloat

class WriteYaml:
  
  def __init__(self) -> None:
    """Constructor WriteYaml class
    """    
    #path info extraction
    self.path = str(pathlib.Path(__file__).parent.resolve())+'/'
    self.path.replace('\\', '/')
    
  
  def dict_to_yaml(self, file_name, dict_file, parents=None, dst_file = None):
    """Read the data from the form dictionary and save it in the corresponding .yml file

    Args:
        file_name (str): file path to write
        dict_file (python dic): form data request
    """    
    dict_file = dict([(k, v) for k, v in dict_file.items() if len(v) > 0])
    yaml = ruamel.yaml.YAML()
    try:
      file_name_path = self.path+file_name
      with open(file_name_path) as fp:
        data_file = yaml.load(fp)
      #print("######################################")
      #print(data_file)
      if not parents == None:
        #print("INCLUYE PARENTS")
        for parent in parents:
          data_aux = data_file['/**']['ros__parameters'][parent]
          #print("######################################")
          #print(file_name_path)
          #print(data_aux)
          for key in dict_file:
            if type(data_aux[key]) == type(True):
              data_aux[key] = dict_file[key].lower() in ['true']
            elif type(data_aux[key]) == type(12):
              data_aux[key] = int(dict_file[key])
            elif type(data_aux[key]) == ScalarFloat:
              data_aux[key] = float(dict_file[key])
            else:
              data_aux[key] = str(dict_file[key])
          data_file['/**']['ros__parameters'][parent] = data_aux
        with open(file_name_path, 'w') as fp:
          yaml.dump(data_file, fp)
      else:
        for key in dict_file:
          #print(key, dict_file[key])
          
          if type(data_file[key]) == type(True):
            data_file[key] = dict_file[key].lower() in ['true']
          elif type(data_file[key]) == type(12):
            data_file[key] = int(float(dict_file[key]))
          elif type(data_file[key]) == ScalarFloat:
            data_file[key] = float(dict_file[key])
          else:
            data_file[key] = str(dict_file[key])
        with open(file_name_path, 'w') as fp:
          yaml.dump(data_file, fp)
      
      if not dst_file == None:
        shutil.copyfile(file_name_path, dst_file)
    except (TypeError, FileNotFoundError, KeyError) as e:
      print(e)
      return False, e.args
    return True, file_name


  
  def yaml_to_dict(self, file_name, key_out, parents=None):
    """Read the data from the form dictionary and save it in the corresponding .yml file

    Args:
        file_name (str): file path to write
    """   
    yaml = ruamel.yaml.YAML()
    try:
      file_name_path = self.path+file_name
      with open(file_name_path) as fp:
        data_file = yaml.load(fp)
      #print("######################################")
      #print(data_file)
      data_out =  data_file[key_out]
     
    except (TypeError, FileNotFoundError, KeyError) as e:
      print(e)
      #return False, e.args
      return False, ""
    #return True, file_name
    return True, data_out
  

  
  def yaml_to_dict_parent(self, file_name, key_out, parents="general"):
    """Read the data from the form dictionary and save it in the corresponding .yml file

    Args:
        file_name (str): file path to write
    """   
    yaml = ruamel.yaml.YAML()
    try:
      file_name_path = self.path+file_name
      with open(file_name_path) as fp:
        data_file = yaml.load(fp)
      
      data_out =  data_file[parents][key_out]
     
    except (TypeError, FileNotFoundError, KeyError) as e:
      print(e)
      #return False, e.args
      return False, ""
    #return True, file_name
    return True, data_out

  def yaml_to_dict_general(self, file_name, parents=False):
      """Read the data from the form dictionary and save it in the corresponding .yml file

      Args:
          file_name (str): file path to write
      """   
      yaml = ruamel.yaml.YAML()
      data_out = {}

      try:
          file_name_path = self.path+file_name
          with open(file_name_path) as fp:
              data_file = yaml.load(fp)
          
          if parents:
          
              data_main = data_file['/**']['ros__parameters']
              
              for parent in data_main:
                  data_aux = data_file['/**']['ros__parameters'][parent]
                  for key in data_aux:
                      data_out[key] =  data_aux[key]
          else:
              for key in data_file:
                  data_out[key] =  data_file[key]

          
      except (TypeError, FileNotFoundError, KeyError) as e:
          print(e)
          #return False, e.args
          return False, data_out
      #return True, file_name
      return True, data_out

  def save_costmap(self, steps, maxh, minh):

    file_name = "/home/gelbert2/costmap_ws/src/pointcloud2_to_costmap/config/params.yaml"
    file_name2 = "/home/gelbert2/costmap_ws/src/pointcloud2_to_costmap/config/params2.yaml"

    yaml = ruamel.yaml.YAML()
    with open(file_name) as fp:
      data_file = yaml.load(fp)

    data_file["resolution"] = steps/2.0

    data_file["inflation_radius"] = steps/4.0
    data_file["robot_radius"] = steps/2.0

    data_file["points_scan_sensor"]["max_obstacle_height"] = maxh
    data_file["points_scan_sensor"]["min_obstacle_height"] = minh


    with open(file_name2, 'w') as fp:
      yaml.dump(data_file, fp)



    file_name = "/home/gelbert2/perception_ws/src/gelbert_planner/config/params.yaml"
    file_name2 = "/home/gelbert2/perception_ws/src/gelbert_planner/config/params2.yaml"

    yaml = ruamel.yaml.YAML()
    with open(file_name) as fp:
      data_file = yaml.load(fp)

    data_file["z_filter_max"] = maxh
    data_file["z_filter_min"] = minh


    with open(file_name2, 'w') as fp:
      yaml.dump(data_file, fp)
