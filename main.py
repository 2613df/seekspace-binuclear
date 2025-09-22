###==================== Init ====================###
script_dir="/path/to/scriptdir/" # 【必须修改,以/结尾】
import sys
sys.path.append(script_dir)
from utils import *
import configparser
import os

# load config && mkdirs
proj_name, data_dir, data_paths, num_cores, out_dirs, conf = pipeline.load_config(script_dir)
pipeline.create_directories(*out_dirs)

###==================== Module 01 Preprocess ====================###
log.wt_log("M01","info","Module 01: Preprocess")

# def file path
_outM01_trans = pipeline.get_path(out_dirs[1], file_name=f"trans", file_ext=[".csv"])
data_paths['trans'] = _outM01_trans[".csv"]
outM01_valid = pipeline.get_path(out_dirs[1], file_name=f"valid", file_ext=[".pickle",".json"])
outM01_cleaned = pipeline.get_path(out_dirs[1], file_name=f"cleaned", file_ext=[".pickle",".json"])
outM01_trans = pipeline.get_path(out_dirs[1], file_name=f"trans", file_ext=[".pickle",".json"])
outM01_pairs = pipeline.get_path(out_dirs[1], file_name=f"pairs", file_ext=[".pickle",".csv"])

# calculate transition spatial file & convert spatial file to dict
preprocess.pre_spatial_transition(data_paths['valid'], _outM01_trans)                                                   # 得到初筛过渡的trans.csv: 仅取出uniquelocation accurate cell的行
preprocess.pre_spatial_parallel(data_paths['valid'], outM01_valid, data_type="valid",num_cores=num_cores)               # 将valid umis由csv->dict，以流式并行处理，指数提升处理效率
preprocess.pre_spatial_parallel(data_paths['cleaned'], outM01_cleaned, data_type="cleaned",num_cores=num_cores)         # 将cleaned umis由csv->dict，以流式并行处理，指数提升处理效率
preprocess.pre_spatial_parallel(data_paths['trans'], outM01_trans, data_type="trans",num_cores=num_cores)               # 将trans umis由csv->dict，以流式并行处理，指数提升处理效率

# calculate unique barcode pairs
data_cleaned=pipeline.read_pickle(outM01_cleaned)                                                                       # 全局读取cleaned umis数据字典，避免浪费资源
preprocess.pre_barcode_pairs(data_cleaned,outM01_pairs)                                                                 # 计算任意两个细胞的不重复的cell_barcode对，由cleaned umis数据计算

# construct spatial barcode sorted data
outM01_sbsorted_valid = pipeline.get_path(out_dirs[1], file_name=f"sbsorted_valid", file_ext=[".pickle",".json"])
outM01_sbsorted_cleaned = pipeline.get_path(out_dirs[1], file_name=f"sbsorted_cleaned", file_ext=[".pickle",".json"])
outM01_sbsorted_trans = pipeline.get_path(out_dirs[1], file_name=f"sbsorted_trans", file_ext=[".pickle",".json"])
preprocess.pre_spatial_barcode_sorted(data_paths['valid'],outM01_sbsorted_valid,data_type="valid")                      # 构建以spatial barcode为视角的spatial file，由valid umis数据计算
preprocess.pre_spatial_barcode_sorted(data_paths['cleaned'],outM01_sbsorted_cleaned,data_type="cleaned")                # 构建以spatial barcode为视角的spatial file，由cleaned umis数据计算
preprocess.pre_spatial_barcode_sorted(data_paths['trans'],outM01_sbsorted_trans,data_type="trans")                      # 构建以spatial barcode为视角的spatial file，由trans umis数据计算
# 
