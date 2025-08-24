import csv
import os
from typing import List, Dict, Any, Optional

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
                description: str, id_val: Optional[str], keep_compatible: bool, 
                curve_file: Optional[str]):
        """向 scenario_list 添加一行数据。"""
        # 将布尔值转为大写字符串以匹配常见CSV格式
        keep_compatible_str = str(keep_compatible).upper()
        
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
        self._data_columns: Dict[str, List[Any]] = {}

    def set_input_column(self, data: List[str]):
        """设置第一列 'input' 的数据。"""
        if not self._input_column:
            self._input_column = data

    def add_column(self, column_name: str, data: List[Any]):
        """按列添加一个 scenario 的数据。"""
        self._data_columns[column_name] = data

    def save_to_csv(self, filepath: str):
        """将数据重构并保存为 CSV 文件。"""
        print(f"正在保存 scenario_settings 数据到 {filepath}...")
        if not self._input_column:
            print("错误：'input' 列数据为空，无法保存 scenario_settings.csv。")
            return
            
        # 按列名排序以确保输出顺序一致
        sorted_column_names = sorted(self._data_columns.keys())
        headers = ['input'] + sorted_column_names

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
                # 逐行写入数据
                for i, input_name in enumerate(self._input_column):
                    row = [input_name]
                    for col_name in sorted_column_names:
                        # 确保数据列长度足够
                        if i < len(self._data_columns[col_name]):
                            row.append(self._data_columns[col_name][i])
                        else:
                            row.append('') # 如果某列数据缺失则填空
                    writer.writerow(row)
            print("scenario_settings.csv 保存成功。")
        except IOError as e:
            print(f"错误：无法写入文件 {filepath}。原因: {e}")


def process_data(all_var_path: str, param_encoding_path: str):
    """
    主处理函数，执行所有数据转换步骤。
    """
    # 1. 初始化
    print("开始处理数据...")
    scenario_list = ScenarioList()
    scenario_settings = ScenarioSettings()

    # 2. 创建输出目录
    output_dir = 'input'
    os.makedirs(output_dir, exist_ok=True)

    # 3. 读取并解析 all_var.csv
    full_data = []
    special_types_dict = {}
    print(f"正在读取 {all_var_path}...")
    try:
        with open(all_var_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过表头
            for i, row in enumerate(reader):
                if len(row) < 21 or not row[20]:  # 检查U列非空
                    continue

                is_variable = 1 if row[1].strip() != 'Static' else 0
                
                val_f = None
                val_m = None

                # 根据更新后的逻辑填充 F 和 M 列
                if is_variable == 0: # 如果是 Static
                    val_f = row[5].strip()
                    try:
                        val_m_str = row[12].strip().replace('%', '')
                        val_m = float(val_m_str) if val_m_str else None
                    except (ValueError, IndexError):
                        val_m = None
                
                item_a = int(row[0].strip())
                item_t = row[19].strip()
                
                full_data.append([
                    item_a,              # 0: A列 index
                    is_variable,         # 1: B列 是否变量 (0 or 1)
                    val_f,               # 2: F列 (按新逻辑)
                    val_m,               # 3: M列 (按新逻辑)
                    item_t,              # 4: T列 特殊类型
                    row[20].strip()      # 5: U列 数据库项名称
                ])

                # 填充特殊类型字典
                if item_t:
                    if item_t not in special_types_dict:
                        special_types_dict[item_t] = []
                    special_types_dict[item_t].append(item_a)

    except FileNotFoundError:
        print(f"错误: 输入文件 {all_var_path} 未找到。")
        return
    except Exception as e:
        print(f"处理 {all_var_path} 时发生错误: {e}")
        return
    print(f"{all_var_path} 读取完毕，共处理 {len(full_data)} 条有效数据。")

    # 4. 读取 param_encoding.csv
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
    if len(param_data) > 1:
        for i, row in enumerate(param_data[1:], start=1):
            try:
                # A列必须是整数
                full_data_index = int(row[0].strip())
                valid_param_rows.append({'row_index': i, 'full_data_index': full_data_index})
            except (ValueError, IndexError):
                continue
    
    # 将数据转置以便按列遍历
    transposed_param_data = list(map(list, zip(*param_data)))

    # 5. 遍历 scenario 列并生成数据
    if len(transposed_param_data) < 2:
        print("警告: param_encoding.csv 中没有找到 scenario 数据列。")
    else:
        # 从第二列开始遍历
        for k, column_data in enumerate(transposed_param_data[1:]):
            if len(column_data) < 2 or not column_data[1].strip():
                break # 如果列第二行为空，则停止

            scenario_name = f"sample_{k}"
            print(f"正在处理 scenario: {scenario_name}...")
            
            # a. 初始化 sample_data (使用静态、非特殊类型数据)
            sample_data = []
            for item in full_data:
                # item[1] == 0 表示 Static, item[4] == '' 表示特殊类型为空
                if item[1] == 0 and not item[4]:
                    sample_data.append([item[5], item[3]]) # [数据库名, 初始值]

            # b. 添加变量修改
            for param_info in valid_param_rows:
                db_name = None
                # 通过索引在 full_data 中查找数据库名
                for item in full_data:
                    if item[0] == param_info['full_data_index']:
                        db_name = item[5]
                        break
                
                if db_name:
                    db_val = column_data[param_info['row_index']].strip()
                    sample_data.append([db_name, db_val])

            # c. 更新 scenario_list
            scenario_list.add_row(
                short_name=scenario_name,
                title="Scenario_sample",
                area_code="UK_united_kingdom",
                end_year="2020",
                description="sample",
                id_val=None,
                keep_compatible=False,
                curve_file=None
            )

            # d. 更新 scenario_settings
            db_names = [row[0] for row in sample_data]
            db_values = [row[1] for row in sample_data]
            
            if k == 0:
                scenario_settings.set_input_column(db_names)
            
            scenario_settings.add_column(scenario_name, db_values)

    # 6. 保存最终结果
    scenario_list.save_to_csv(os.path.join(output_dir, 'scenario_list.csv'))
    scenario_settings.save_to_csv(os.path.join(output_dir, 'scenario_settings.csv'))
    
    print("\n所有处理已完成！")


if __name__ == '__main__':
    # 定义输入文件名
    all_var_file = 'all_var.csv'
    param_encoding_file = 'param_encoding.csv'

    # 执行主函数
    process_data(all_var_file, param_encoding_file)