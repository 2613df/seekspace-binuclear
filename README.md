# seekspace-binuclear

面向寻因空间转录组数据 (seekspace)，基于“双重锁定法”识别同源双核对的小工具。

本工具仅是临时兴起，如有意使用或参阅，还请您附上这个项目



### 你可能想知道

1. 能用来干什么？
   
   找出来自同一细胞的双核。

2. 适用于seekspace以外的数据吗？
   
   seekspace可以通俗理解为单核测序 + 打空间位置标签，也就是给每个细胞(核)打上他的位置标签。这种位置标签在一个细胞(核)里并不唯一，seekspaceTool v1.0会通过一系列手段，在确定有效标签后再重新计算出其可靠位置。我们正是使用该seekspaceTool过程中产生的文件来进行同源双核的匹配的。所以理论上，只要是类似原理的测序数据都可以作为输入，只是您需要自行阅读代码，跳过专为seekspace所设计的部分，并构筑可用的输入[用AI]。

3. 我需要准备什么数据？
   
   您需要自行跑一遍 seekspaceTool，获得输出结果，结构大致如下：
   
   `${data_dir}`/Analysis/Spatial_Positioning/
   
   `${data_dir}`/Analysis/scRNA-seq_Analysis/
   
   `${data_dir}`/Analysis/Tissue_Detection/

4. 思路是什么？
   
   [推测] 按照seekspace透膜原理，推测同一个细胞内的不同核所含的空间位置标签，在种类上应该是相似的，且有一定重叠。在此基础上设阈值、筛空间邻近，即 空间标签相似 + 空间距离接近 的“双重锁定”法，来找到相对可靠的同源双核对。
   
   临时兴起，思路不完善，有意完善还请提issue，有意使用还请附上项目



### 慢速上手

1. 其他需要准备的
   
   一个高级些的AI：善用AI解决可能的报错
   
   已经使用SeekspaceTool跑完的数据，输出结果的结构大致如下：
   
   `输出路径`/Analysis/Spatial_Positioning/
   
   `输出路径`/Analysis/scRNA-seq_Analysis/
   
   `输出路径`/Analysis/Tissue_Detection/
   
   记住`输出路径`所指代的具体目录，后续要填入conf.ini

2. 安装与环境
   
   Python >=3.9
   
   `pip install pandas tqdm configparser`

3. 编辑conf.ini
   
   ```ini
   # data_dir: 填入在第一步获取的 输出路径 所对应的具体值，以 / 结尾
   data_dir=/path/to/your/toolout/
   # proj_name: 你在SeekspaceTool中指定的Proj_name,如果不知道就看/输出路径/Analysis/scRNA-seq_Analysis/xxx_summary.csv【这里xxx就是proj_name】
   proj_name=liver5
   # out_dir: 本工具产出的目录名，这个文件夹会保存到与 /输出路径/Analysis 同级
   out_dir=CalcR1
   out_01=01_prepross
   out_02=02_overlapRatio
   out_03=03_eudisPlot
   out_04=04_filter
   out_05=05_noise
   # num_cores: 多核，量力而为
   num_cores=8
   ```

4. 设置脚本的根路径，在`main.py` #2，以 / 结尾
   
   ```python
   script_dir="/path/to/scriptdir/"
   ```

5. 运行
   
   ```bash
   python /path/to/scriptdir/main.py
   ```

6. 程序会
   
   ① 生成 valid / cleaned / trans 的空间标签文件[valid是所有有效空间标签、cleaned是所有纳入位置计算的有效空间标签、trans为过渡文件]。
   
   ② 分别构建以cell_barcode和spatial_barcode为视角聚合的结果
   
   ③ 根据空间标签集合的相似度(overlap / jaccard / UMI加权)、空间距离(欧式距离)，共同筛选为候选的同源双核对



### License

本项目采用 **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International（CC BY-NC-SA 4.0）** 许可证。

简单来说：仅供学术探讨，还请署名，不要商用，虽然我也不觉得能商用。



### Citation

若本项目对你的研究或工具链有帮助，还请引用：

> Xiaozhi. seekspace-binuclear. GitHub repository. Available at: https://github.com/2613df/seekspace-binuclear/ (accessed September 23, 2025).
