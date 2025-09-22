from .common import *
from .log import * 
import pandas as pd
import pickle
import json
import multiprocessing as mp
import os
from tqdm import tqdm
import gzip

def process_chunk(chunk, data_type):
    """
    @description: 处理每个数据块，根据数据类型（valid 或 cleaned）决定处理的字段
    @param {pd.DataFrame} chunk: 数据块
    @param {str} data_type: 数据类型，"valid" 或 "cleaned"
    @return {dict}: 处理后的数据
    """
    try:
        grouped_data = {}
        current_group = {
            "UMIs": [],
            "Spatial_Barcodes": [],
            "X": [],
            "Y": []
        }

        if data_type == "valid":
            current_group.update({
                "isUniqueLocation": [],
                "isAccurate": [],
                "isCell": []
            })

        current_cell_barcode = None

        for _, row in chunk.iterrows():
            cell_barcode = row['Cell_Barcode']
            if cell_barcode != current_cell_barcode and current_cell_barcode is not None:
                # Store the current group and start a new one
                grouped_data[current_cell_barcode] = current_group
                current_group = {
                    "UMIs": [],
                    "Spatial_Barcodes": [],
                    "X": [],
                    "Y": []
                }
                if data_type == "valid":
                    current_group.update({
                        "isUniqueLocation": [],
                        "isAccurate": [],
                        "isCell": []
                    })

            # Update current cell barcode
            current_cell_barcode = cell_barcode

            # Append data to the current group
            current_group['UMIs'].append(row['UMI'])
            current_group['Spatial_Barcodes'].append(row['Spatial_Barcode'])
            current_group['X'].append(row['X'])
            current_group['Y'].append(row['Y'])

            if data_type == "valid":
                current_group['isUniqueLocation'].append(row['isUniqueLocation'])
                current_group['isAccurate'].append(row['isAccurate'])
                current_group['isCell'].append(row['isCell'])

        if current_cell_barcode is not None:
            grouped_data[current_cell_barcode] = current_group

        return grouped_data
    except Exception as e:
        print(f"Error in process_chunk: {e}")
        return {}

def pre_spatial_parallel(file_path, out_paths, data_type="valid", chunksize=5000, num_cores=8):
    """
    @description: 使用多进程预处理 spatial UMIs 数据
    @param {str} file_path: 输入 CSV 文件路径
    @param {dict} out_paths: 输出文件路径字典（pickle 和 json）
    @param {str} data_type: 数据类型，"valid" 或 "cleaned"
    @param {int} chunksize: 每个进程读取和处理的行数
    @param {int} num_cores: 并行处理的进程数
    @return {bool} True if successful
    """

    wt_log(__name__,"info",f"Start: Convert {data_type} to dict.")
    if(check_files_exist(out_paths))==True :
        wt_log(__name__,"info",f"Skip: dealed {data_type} files exist.")
        return
    wt_log(__name__,"info","====== Initialize")

    if file_path.endswith(".gz"):
        opener = gzip.open
    else:
        opener = open
    
    with opener(file_path, 'rt') as f:
        total_lines = sum(1 for _ in f) - 1
    total_chunks = total_lines // chunksize + 1
    wt_log(__name__,"info","====== Process, it takes time. (Hours needed)")
    pool = mp.Pool(processes=num_cores)
    
    results = []
    with pd.read_csv(file_path, chunksize=chunksize) as reader, tqdm(total=total_chunks, desc="Processing") as pbar:
        for chunk in reader:
            result = pool.apply_async(process_chunk, args=(chunk, data_type), callback=lambda _: pbar.update(1))
            results.append(result)

    pool.close()
    pool.join()

    def merge_grouped_data(results):
        merged_grouped_data = {}

        for grouped_data in results:
            for cell_barcode, cell_data in grouped_data.items():
                if cell_barcode in merged_grouped_data:
                    for key, value in cell_data.items():
                        if isinstance(value, list):
                            merged_grouped_data[cell_barcode][key].extend(value)
                        else:
                            merged_grouped_data[cell_barcode][key] = value
                else:
                    merged_grouped_data[cell_barcode] = cell_data

        return merged_grouped_data
    wt_log(__name__,"info","====== Refine")
    results_data = [result.get() for result in results]
    merged_grouped_data = merge_grouped_data(results_data)
    wt_log(__name__,"info","====== Save")

    save_file(merged_grouped_data, out_paths)

    return True

def pre_spatial_single(file_path, out_paths, data_type="valid"):
    """
    @description: 预处理 spatial UMIs 数据，并根据数据类型（valid 或 cleaned）决定处理的字段
    @param {str} file_path: 输入 CSV 文件路径
    @param {dict} out_pickle: 输出 pickle 文件路径
    @param {str} out_json: 输出 JSON 文件路径
    @param {str} data_type: 数据类型，"valid" 或 "cleaned"，决定是否处理特定字段
    @return {bool} True if successful
    """

    wt_log(__name__,"info",f"Start dealing with {data_type} spatial files")

    import pandas as pd
    import json
    import pickle
    if(check_files_exist(out_paths))==True :
        wt_log(__name__,"info","Skip: dealed spatial file exist.")
        return
    wt_log(__name__,"info","====== Dealing with spatial files, it takes time. (Hours needed)")
    with pd.read_csv(file_path, chunksize=1000) as reader:
        current_cell_barcode = None
        current_group = {
            "UMIs": [],
            "Spatial_Barcodes": [],
            "X": [],
            "Y": []
        }

        if data_type == "valid":
            current_group.update({
                "isUniqueLocation": [],
                "isAccurate": [],
                "isCell": []
            })

        grouped_data = {}

        for chunk in reader:
            for index, row in chunk.iterrows():
                cell_barcode = row['Cell_Barcode']
                if cell_barcode != current_cell_barcode and current_cell_barcode is not None:
                    # Store the current group and start a new one
                    grouped_data[current_cell_barcode] = current_group
                    current_group = {
                        "UMIs": [],
                        "Spatial_Barcodes": [],
                        "X": [],
                        "Y": []
                    }
                    if data_type == "valid":
                        current_group.update({
                            "isUniqueLocation": [],
                            "isAccurate": [],
                            "isCell": []
                        })

                # Update current cell barcode
                current_cell_barcode = cell_barcode

                # Append data to the current group
                current_group['UMIs'].append(row['UMI'])
                current_group['Spatial_Barcodes'].append(row['Spatial_Barcode'])
                current_group['X'].append(row['X'])
                current_group['Y'].append(row['Y'])

                if data_type == "valid":
                    current_group['isUniqueLocation'].append(row['isUniqueLocation'])
                    current_group['isAccurate'].append(row['isAccurate'])
                    current_group['isCell'].append(row['isCell'])

        # Store the last group
        if current_cell_barcode is not None:
            grouped_data[current_cell_barcode] = current_group

        # Save data to pickle and JSON files
        wt_log(__name__,"info","====== Saving dealed spatial files.")
        save_file(grouped_data,out_paths)
        return True

def pre_barcode_pairs(spatial_umis_cleaned,out_paths):
    import pickle
    import pandas as pd
    from itertools import combinations
    import gc
    #unique_barcodes = spatial_umis['Cell_Barcode'].unique()
    wt_log(__name__,"info",f"Start: Calculate unique barcode pairs.")
    if(check_files_exist(out_paths))==True :
        wt_log(__name__,"info","Skip: barcode pairs files exist.")
        return
    wt_log(__name__,"info","====== Process, it takes time. (Hours needed)")
    unique_barcodes = pd.Series(list(spatial_umis_cleaned.keys())).unique()
    # Create barcode pairs
    barcode_pairs = list(combinations(unique_barcodes, 2))
    wt_log(__name__,"info","====== Save")
    save_file(barcode_pairs,out_paths,csv_mode="bcpr")
    return True

def pre_spatial_transition(file_path, out_paths, filter_accurate=1):
    wt_log(__name__,"info",f"Start: Calculate transition spatial files.")
    if(check_files_exist(out_paths))==True :
        wt_log(__name__,"info","Skip: transition files exist.")
        return
    wt_log(__name__,"info","====== Process")
    import pandas as pd
    data=pd.read_csv(file_path)
    if filter_accurate==1:
        data = data[(data["isUniqueLocation"] == 1) & (data["isAccurate"] == 1) & (data["isCell"] == 1)]
    else:
        data = data[(data["isUniqueLocation"] == 1) & (data["isCell"] == 1)]
    wt_log(__name__,"info","====== Save")
    data.to_csv(out_paths[".csv"],index=False,quoting=False)
    return True

def pre_spatial_barcode_sorted(file_path, out_paths, data_type="valid"):
    wt_log(__name__,"info",f"Start: Construct {data_type} spatial_barcode sorted data.")
    if(check_files_exist(out_paths))==True :
        wt_log(__name__,"info",f"Skip: {data_type} spatial_barcode sorted files exist.")
        return
    wt_log(__name__,"info","====== Process, it takes time. (Hours needed)")

    grouped_data = {}
    
    with pd.read_csv(file_path, chunksize=1000) as reader:
        for chunk in reader:
            chunk = chunk.sort_values(by='Spatial_Barcode')
            
            for index, row in chunk.iterrows():
                spbc = row['Spatial_Barcode']
                
                if spbc not in grouped_data:
                    grouped_data[spbc] = {
                        'cellCounts_ab': 0,
                        'cellCounts_un': 0,
                        'X': row['X'],
                        'Y': row['Y'],
                        'cellbc': [],
                        'cellbc_countsInCell': [],
                        'raw': []
                    }
                
                grouped_data[spbc]['cellCounts_ab'] += 1
                
                if data_type=="valid":
                    raw_row = ','.join([str(row['Cell_Barcode']), str(row['UMI']), str(row['Spatial_Barcode']),
                                        str(row['isUniqueLocation']), str(row['isAccurate']), str(row['isCell']),
                                        str(row['X']), str(row['Y'])])
                else:
                    raw_row = ','.join([str(row['Cell_Barcode']), str(row['UMI']), str(row['Spatial_Barcode']),
                                        str(row['X']), str(row['Y'])])
                grouped_data[spbc]['raw'].append(raw_row)
                
                cell_barcode = row['Cell_Barcode']
                if cell_barcode not in grouped_data[spbc]['cellbc']:
                    grouped_data[spbc]['cellbc'].append(cell_barcode)
                    grouped_data[spbc]['cellbc_countsInCell'].append(1)
                    grouped_data[spbc]['cellCounts_un'] += 1
                else:
                    idx = grouped_data[spbc]['cellbc'].index(cell_barcode)
                    grouped_data[spbc]['cellbc_countsInCell'][idx] += 1
    wt_log(__name__,"info","====== Save")
    save_file(grouped_data,out_paths)
    return True