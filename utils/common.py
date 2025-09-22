from .log import *

def convert_set_to_list(obj):
    if isinstance(obj, dict):
        return {k: convert_set_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_set_to_list(i) for i in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj

def norm_savefile(data, out_pickle="no", out_json="no", out_csv="no"):
    #depreciated
    import pickle
    import json
    import csv
    if(out_pickle!="no"):
        with open(out_pickle, 'wb') as f:
            pickle.dump(data, f)
    if(out_json!="no"):
        def convert_set_to_list(obj):
            if isinstance(obj, dict):
                return {k: convert_set_to_list(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_set_to_list(i) for i in obj]
            elif isinstance(obj, set):
                return list(obj)
            else:
                return obj
        data_list = convert_set_to_list(data)
        with open(out_json, 'w') as f:
            json.dump(data_list, f)
    if out_csv != "no":
        with open(out_csv, 'w', newline='') as f:
            if isinstance(data, dict):
                example_key = next(iter(data))
                fieldnames = ['Spatial_Barcode'] + list(data[example_key].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for spbc, values in data.items():
                    row = {'Spatial_Barcode': spbc}
                    row.update(values)
                    writer.writerow(row)
            else:
                print("Warning: CSV保存失败，data 格式不正确。")

def commontest():
    print("common loaded")

def save_file(data, file_paths, csv_mode="spbc"):
    """
    @description: 根据传入的文件路径字典，保存数据到不同的文件格式
    @param {dict} file_paths: 包含文件扩展名和路径的字典（如 {'.pickle': 'path_to_pickle', '.json': 'path_to_json'}）
    """
    import pickle
    import json
    import csv
    import os

    for ext, path in file_paths.items():
        if ext == '.pickle':
            with open(path, 'wb') as f:
                pickle.dump(data, f)
        
        elif ext == '.json':
            def convert_set_to_list(obj):
                if isinstance(obj, dict):
                    return {k: convert_set_to_list(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_set_to_list(i) for i in obj]
                elif isinstance(obj, set):
                    return list(obj)
                else:
                    return obj
            data_list = convert_set_to_list(data)
            with open(path, 'w') as f:
                json.dump(data_list, f)
        
        elif ext == '.csv':
            if csv_mode == "spbc":
                with open(path, 'w', newline='') as f:
                    if isinstance(data, dict):
                        example_key = next(iter(data))
                        fieldnames = ['Spatial_Barcode'] + list(data[example_key].keys())
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()

                        for spbc, values in data.items():
                            row = {'Spatial_Barcode': spbc}
                            row.update(values)
                            writer.writerow(row)
                    else:
                        wt_log(__name__,"warning","CSV保存失败，data 格式不正确")
            elif csv_mode == "bcpr":
                with open(path, "w") as file:
                    for item in data:
                        file.write(str(item[0]) + "," + str(item[1]) + "\n")
            else:
                with open(path, "w") as file:
                    for item in data:
                        file.write(str(item)+"\n")
        else:
            wt_log(__name__,"warning",f"不支持的文件格式: {ext}")

def check_files_exist(paths):
    """
    @description: 检查传入的路径是否都存在
    @param {str/dict} paths: 单个文件路径的字符串或包含多个路径的字典（字典的 value 应为路径）
    @return {bool}: 如果所有路径存在返回 True，否则返回 False
    """

    import os

    if isinstance(paths, str):
        return os.path.isfile(paths)
    elif isinstance(paths, dict):
        return all(os.path.isfile(path) for path in paths.values())
    else:
        wt_log(__name__,"error","输入类型不正确，必须为字符串或字典")
        return False