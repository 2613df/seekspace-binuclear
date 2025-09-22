import configparser
import os
from .common import *

def load_config(script_dir):
    """
    @description: 读取conf.ini中的核心参数
    @param {str} script_dir: 脚本main.py所在目录
    @return {str} proj_name: 项目名
    @return {str} data_dir: seekspaceTools数据输出目录 (含Analysis,Outs等文件夹)
    @return {str} num_cores: 多核运行时所用核心数
    @return {configparser.ConfigParser} conf: 其他参数
    @return {list} out_dirs: binuTools数据输出目录 (即本脚本的输出目录)
    """

    conf = configparser.ConfigParser()
    conf.read(os.path.join(script_dir, "conf.ini"))
    
    proj_name = conf['GLOBAL']['proj_name']
    data_dir = conf['GLOBAL']['data_dir']
    data_paths={}
    data_paths["valid"]=os.path.join(data_dir,"Analysis/Spatial_Positioning/",f"{proj_name}_valid_spatial_umis.csv.gz")
    data_paths["cleaned"]=os.path.join(data_dir,"Analysis/Spatial_Positioning/",f"{proj_name}_spatial_umis_cleaned.csv.gz")
    data_paths["loc"]=os.path.join(data_dir,"Analysis/Spatial_Positioning/",f"{proj_name}_cell_locations.csv")
    data_paths["locFn"]=os.path.join(data_dir,"Outs/demo_filtered_feature_bc_matrix/",f"cell_locations.tsv.gz")
    num_cores = int(conf['GLOBAL']['num_cores'])
    
    out_dirs = [os.path.join(data_dir, conf['GLOBAL']['out_dir'])]
    out_dirs += [os.path.join(out_dirs[0], conf['GLOBAL'][key]) for key in conf['GLOBAL'] if key.startswith('out_0')]

    return proj_name, data_dir, data_paths, num_cores, out_dirs, conf


def create_directories(*paths):
    """
    @description: 创建目录
    @param {array} paths: 多个路径
    """
    
    for path in paths:
        os.makedirs(path, exist_ok=True)

def get_path(base_dir, *subdirs, file_name=None, file_ext=None):
    """
    @description: 生成路径并创建目录
    @param {str} base_dir: 根目录
    @param {array} subdirs: 子目录，可以传递多个子目录
    @param {str} file_name: 可选，文件名
    @param {str/list} file_ext: 可选，文件扩展名（如 `.csv`, `.json` 等）
    @return {str/list}: 一个或多个完整路径（如果提供了多个扩展名，则返回多个路径）
    """

    full_path = os.path.join(base_dir, *subdirs)

    if file_name and file_ext:
        return {ext: os.path.join(full_path, f"{file_name}{ext}") for ext in file_ext}
    
    return full_path

def read_pickle(file_paths):
    import pickle
    for ext, path in file_paths.items():
        if ext == '.pickle':
            try:
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                return data
            except Exception as e:
                wt_log(__name__,"error",f"read pickle error, details: {e}")
                return
        else:
            wt_log(__name__,"error",f"read pickle error, details: ext error.")
            return