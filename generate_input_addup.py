import csv
import copy
import os
from typing import List, Dict, Any, Optional


def is_float(value):
    if type(value) == float:
        return True
    try:
        float(value.replace(',',''))
        return True
    except:
        return False

def dfs_search(dict,key,is_min:bool):
    value = None
    if key not in dict.keys():
        return
    if key == "SYN.20":
        print(dict[key])
    if is_min:
        value = dict[key]["min_value"]
    else:
        value = dict[key]["max_value"]
    if is_float(value):
        if type(value)==float:
            return value
        else:
            return float(value.replace(',',''))
    else:
        if type(value) == str and value.split('.')[0] == "VAR":
            id = value.split('.')[1]
        else:
            id = value
        return dfs_search(dict,id,is_min)

class ScenarioList:
    """
    管理 scenario_list.csv 的数据和操作。
    """
    def __init__(self):
        self._headers = [
            'short_name', 'title', 'area_code', 'end_year', 'description', 
            'id', 'keep_compatible', 'curve_file'
        ]
        self._data: List[Dict[str, Any]] = []

    def add_row(self, short_name: str, title: str, area_code: str, end_year: str,
                description: str, id_val: Optional[str], keep_compatible: str, 
                curve_file: Optional[str]):
        """向 scenario_list 添加一行数据。"""
        # 将布尔值转为大写字符串以匹配常见CSV格式
        keep_compatible_str = str(keep_compatible)
        
        # 将 None 值转换为空字符串
        row_dict = {
            'short_name': short_name or '',
            'title': title or '',
            'area_code': area_code or '',
            'end_year': end_year or '',
            'description': description or '',
            'id': id_val or '',
            'keep_compatible': keep_compatible_str,
            'curve_file': curve_file or ''
        }
        self._data.append(row_dict)

    def save_to_csv(self, filepath: str):
        """将数据保存到 CSV 文件。"""
        print(f"正在保存 scenario_list 数据到 {filepath}...")
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self._headers)
                writer.writeheader()
                writer.writerows(self._data)
            print("scenario_list.csv 保存成功。")
        except IOError as e:
            print(f"错误：无法写入文件 {filepath}。原因: {e}")

class ScenarioSettings:
    """
    管理 scenario_settings.csv 的数据和操作。
    """
    def __init__(self):
        self._input_column: List[str] = []
        self._data_columns: List[List[Any]] = []

    def set_input_column(self, data: List[str]):
        """设置第一列 'input' 的数据。"""
        if not self._input_column:
            self._input_column = data

    def add_column(self, column_name: str, data: List[Any]):
        """按列添加一个 scenario 的数据。"""
        self._data_columns[column_name] = data
    
    def convert(self, scenario_name_list: List[str], scaneria_data: Dict[str, List[Any]],scanerio_minmax: Dict[str, Dict[str, Any]],minmax_index_var_id_hash: Dict[str, int]):
        min_max_error_index = []
        self._input_column = scenario_name_list
        for key in scaneria_data.keys():
            scaneria_data_item_copy = copy.deepcopy(scaneria_data[key])
            scaneria_data[key] = [min(scanerio_minmax[key]["max_value"], value) for value in scaneria_data[key]]
            scaneria_data[key] = [max(scanerio_minmax[key]["min_value"], value) for value in scaneria_data[key]]
            # 检查数据是否因为 min/max 限制而发生变化
            if scaneria_data_item_copy != scaneria_data[key]:
                min_max_error_index.append([minmax_index_var_id_hash[key], key])
            self._data_columns.append([key,scaneria_data[key]])
        # 保存 min_max_error_index 到 CSV 文件
        if min_max_error_index:
            error_filepath = "query/min_max_errors.csv"
            try:
                with open(error_filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['index', 'variable_name'])  # 写入表头
                    writer.writerows(min_max_error_index)  # 写入错误数据
                print(f"min_max_errors.csv 保存成功到 {error_filepath}")
            except IOError as e:
                print(f"错误：无法写入文件 {error_filepath}。原因: {e}")
        print(min_max_error_index)
        
    def extra_dict(self,len_column):        
        interconnection_header = "electricity_interconnector"
        interconnection_value_type = ["capacity","import_availability","export_availability","co2_emissions_present","co2_emissions_future","marginal_costs"]
        interconnection_id = ["1","2","3","4","5","6","7","8","9","10","11","12"]
        interconnection_dict = {}
        interconnection_value = [0,0,0,0,0,0.1]
        for i in range(len(interconnection_value_type)):
            for id in interconnection_id:
                interconnection_dict[interconnection_header+f"_{id}_"+interconnection_value_type[i]] = [interconnection_value[i]] * len_column
        return interconnection_dict


    def save_to_csv(self, filepath: str,add_extra_data:bool=True):
        """将数据重构并保存为 CSV 文件。"""
        print(f"正在保存 scenario_settings 数据到 {filepath}...")
        if not self._input_column:
            print("错误：'input' 列数据为空，无法保存 scenario_settings.csv。")
            return
            
        # 按列名排序以确保输出顺序一致
        column_names = self._input_column
        headers = ['input'] + column_names

        # print(self._input_column)
        # for item in self._data_columns:
        #     if len(item[1]) != len(self._input_column):
        #         print(item[0],len(item[1]))
        # return

        

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
                # 逐行写入数据(update的variable数据)
                for i in range(len(self._data_columns)):
                    row = [self._data_columns[i][0]]  # 第一个元素作为 input 列
                    for j in range(1, len(self._data_columns[i])):
                        # if self._data_columns[i][0] == 'buildings_number_of_buildings_future':
                            # print(self._data_columns[i][1])
                        # if len(self._data_columns[i])>1:
                        #     print(self._data_columns[i])
                        # 对变量值进行数值转换，self._data_columns[i][1]是一个包含多个数据的列表
                        data_list = self._data_columns[i][1]
                        for k in range(len(data_list)):
                            converted_value = data_list[k]
                            row.append(converted_value)
                    writer.writerow(row)
                #  写入额外的数据
                if add_extra_data:
                    extra_data_dict = self.extra_dict(len(column_names))
                    for key in extra_data_dict.keys():
                        row = [key]
                        for j in range(0, len(extra_data_dict[key])):
                            row.append(extra_data_dict[key][j])
                        writer.writerow(row)
            print("scenario_settings.csv 保存成功。")
        except IOError as e:
            print(f"错误：无法写入文件 {filepath}。原因: {e}")
def is_special_row(row: List[str],var_no: int) -> bool:
    """
    特殊检查函数，用于判断某一行数据是否需要进行处理。
    
    Args:
        row: CSV文件中的一行数据
        
    Returns:
        bool: True表示需要处理该行，False表示跳过该行
    """
    pass_var = [160,163,170,172,176,177,190,192,196,198,252,253,254,255,674,675,676,677,705,717,924,925,927]
    pass_var1 = list(range(678, 694))
    pass_var2 = list(range(698, 703))
    # print(row)
    if row[8]== 'Interconnector 2 to 12':
        return True
    elif row[9]== 'Merit order':
        return True
    elif row[7]== 'Merit order':
        return True
    elif row[9].startswith('Merit order'):
        return True
    elif var_no in pass_var or var_no in pass_var1 or var_no in pass_var2:
        return True
    elif row[12] == "InVar":
        return True
    else:
        return False

def process_data(all_var_path: str, param_encoding_path: str, database_index_path: str):
    """
    主处理函数，执行所有数据转换步骤。
    """
    # 1. 初始化
    print("开始处理数据...")
    scenario_list = ScenarioList()
    scenario_settings = ScenarioSettings()
    
    database_index = {}
    with open(database_index_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过表头
        for row in reader:
            if len(row) >= 8 and row[7] != '':  # 确保行至少有2列（A和H）
                database_index[int(row[0])] = row[7]  # A列是row[0]，H列是row[7]
    
    # 2. 创建输出目录
    output_dir = 'data/input'
    os.makedirs(output_dir, exist_ok=True)

    # 3. 先读取 param_encoding ,确认 需要修改的变量的var no.
    variable_var_no = []
    print(f"正在读取 {param_encoding_path}并确认需要处理的var no...")
    try:
        with open(param_encoding_path, 'r', encoding='utf-8') as f:
            param_data = list(csv.reader(f))
    except FileNotFoundError:
        print(f"错误: 输入文件 {param_encoding_path} 未找到。")
        return
    except Exception as e:
        print(f"处理 {param_encoding_path} 时发生错误: {e}")
        return

    # 识别 param_encoding 中的有效修改行
    variable_var_no = []
    if len(param_data) > 1:
        for i, row in enumerate(param_data[2:], start=2):
            try:
                # A列必须是整数
                var_no_str = row[0].strip()
                # 处理可能包含 . 分割的变量名，取第一部分的数字
                if '.' in var_no_str:
                    full_data_index = int(var_no_str.split('.')[0])
                else:
                    full_data_index = int(var_no_str)
                variable_var_no.append(full_data_index)
            except (ValueError, IndexError):
                continue
    

    # 5. 读取 param_encoding.csv
    print(f"正在读取 {param_encoding_path}...")
    try:
        with open(param_encoding_path, 'r', encoding='utf-8') as f:
            param_data = list(csv.reader(f))
    except FileNotFoundError:
        print(f"错误: 输入文件 {param_encoding_path} 未找到。")
        return
    except Exception as e:
        print(f"处理 {param_encoding_path} 时发生错误: {e}")
        return

    # 识别 param_encoding 中的有效修改行
    valid_param_rows = []
    min_max_dict={}
    minmax_var_id_index_hash={}
    minmax_index_var_id_hash={}
    if len(param_data) > 1:
        for i, row in enumerate(param_data[1:], start=1):
            try:
                # A列必须是整数
                var_no_str = row[0].strip()
                if var_no_str == "SYNCOM.39":
                    print(row[2],row[3])
                min_max_dict[var_no_str] = {"min_value": row[2], "max_value": row[3]}
                # 处理可能包含 . 分割的变量名，取第一部分的数字
                if '.' in var_no_str:
                    full_data_index = int(var_no_str.split('.')[0])
                elif var_no_str == '' or var_no_str == 'END':
                    break
                else:
                    full_data_index = int(var_no_str)
                min_max_dict[var_no_str] = {"min_value": row[2], "max_value": row[3]}
                # 构建一个hastable, 这是一个子集
                try:
                    id = int(var_no_str.split('.')[0])
                    minmax_var_id_index_hash[id] =  var_no_str
                except:
                    pass

                valid_param_rows.append({'row_index': i, 'full_data_index': full_data_index})
            except (ValueError, IndexError):
                continue
    
    # 这里对minmax_idct，进行深度遍历修改数据
    for key in min_max_dict.keys():
        min_max_dict[key]["min_value"] = dfs_search(min_max_dict,key,True)
        min_max_dict[key]["max_value"] = dfs_search(min_max_dict,key,False)
    # print(min_max_dict)
    # print(minmax_var_id_index_hash)
    # 将 min_max_dict 保存为 CSV 文件
    min_max_csv_path = "query/min_max_data.csv"
    print(f"正在保存 min_max_dict 数据到 {min_max_csv_path}...")
    try:
        with open(min_max_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(['variable_key', 'min_value', 'max_value'])
            # 写入数据
            for id , index in minmax_var_id_index_hash.items():
                key = index
                value_dict = min_max_dict[key]
                writer.writerow([key, value_dict['min_value'], value_dict['max_value']])
        print(f"min_max_dict 数据已保存到 {min_max_csv_path}")
    except IOError as e:
        print(f"错误：无法写入文件 {min_max_csv_path}。原因: {e}")
    # print(minmax_var_id_index_hash)
    # exit()


    # 将数据转置以便按列遍历
    transposed_param_data = list(map(list, zip(*param_data)))

    # 6. 遍历 scenario 列并生成数据
    # 先根据static数据生成一个字典
    scaneria_data = {}
    scanerio_minmax={}
    scanerio_name_list = []
    # for item in static_data:
    #     scaneria_data[item[2]] = []
    for var_no in variable_var_no:
        if var_no in database_index.keys():
            scaneria_data[database_index[var_no]] = []
    if len(transposed_param_data) < 5:
        print("警告: param_encoding.csv 中没有找到 scenario 数据列。")
    else:
        # 从第二列开始遍历
        
        for k, column_data in enumerate(transposed_param_data[4:]):
            #这里其实是要每次遍历一个sample
            if len(column_data) < 2 or  column_data[1].strip() =='':
                break # 如果列第四行为空，则停止

            scenario_name = f"sample_{k}"
            scanerio_name_list.append(scenario_name)
            print(f"正在处理 scenario: {scenario_name}...")
            

            # static 常量添加
            # for item in static_data:
            #     scaneria_data[item[2]].append(item[1])
            # print(scaneria_data)
            
            # 变量添加
            for param_info in valid_param_rows:
                # 通过索引在 full_data 中查找数据库名
                if param_info['full_data_index'] not in database_index.keys():
                    # print(f"not found {param_info['full_data_index']}")
                    continue
                db_name = database_index[param_info['full_data_index']]
                db_val = float(column_data[param_info['row_index']].strip().replace(',',''))
                scaneria_data[db_name].append(db_val)
                
                minmax_index_var_id_hash[db_name] = param_info['full_data_index']
                min_max_index = minmax_var_id_index_hash[param_info['full_data_index']]
                min_value,max_value = min_max_dict[min_max_index]["min_value"],min_max_dict[min_max_index]["max_value"]
                scanerio_minmax[db_name] = {"min_value": min_value, "max_value": max_value}
                if k==0:
                    print("minmax",param_info['full_data_index'],min_value,max_value)

            # c. 更新 scenario_list
            scenario_list.add_row(
                short_name=scenario_name,
                title="Scenario_sample",
                area_code="UK_united_kingdom",
                end_year="2020",
                description="sample",
                id_val="1362080",
                keep_compatible="False",
                curve_file=None
            )
            
        # print(valid_param_rows)
        scenario_settings.convert(scanerio_name_list, scaneria_data,scanerio_minmax,minmax_index_var_id_hash)

    # 6. 保存最终结果
    scenario_list.save_to_csv(os.path.join(output_dir, 'scenario_list.csv'))
    scenario_settings.save_to_csv(os.path.join(output_dir, 'scenario_settings.csv'))
    
    print("\n所有处理已完成！")


if __name__ == '__main__':
    # 定义输入文件名
    all_var_file = 'query/all_var_real.csv'
    param_encoding_file = 'query/param_encoding_real.csv'
    database_index_file = 'query/database_index.csv'

    # 执行主函数
    process_data(all_var_file, param_encoding_file, database_index_file)





    
