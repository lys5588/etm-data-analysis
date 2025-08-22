import csv

def process_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        output_file = "splitted_output.csv"
        with open(output_file, 'a', newline='', encoding='utf-8') as out_csv:
            writer = csv.writer(out_csv)
            for row in reader:
                # 直接对每一列分别处理，比如去除首尾空格
                processed_row = [col.strip() for col in row]
                # 可以按逗号分列（如果原始数据是逗号分隔的），这里假设每个单元格内可能还有逗号
                # 如果需要进一步分列，可以对每个单元格再 split
                # 例如：将每个单元格按逗号再分列，然后展平成一行
                splitted = []
                for col in processed_row:
                    splitted.extend(col.split(','))
                writer.writerow(splitted)

def convert_semicolon_to_comma(input_csv_path, output_csv_path):
    """
    读取 input_csv_path，将其中的 ; 替换为 , 并保存到 output_csv_path。
    适用于需要将分号分隔的CSV转换为逗号分隔的CSV。
    """
    with open(input_csv_path, 'r', encoding='utf-8') as infile, \
         open(output_csv_path, 'w', encoding='utf-8', newline='') as outfile:
        for line in infile:
            # 将每一行的分号替换为逗号
            new_line = line.replace(';', ',')
            outfile.write(new_line)




# Example usage:
# win /f/repository/project/Own/etm-data-analysis/slider_setting
# 检查路径是否正确（Windows环境下建议使用反斜杠或原始字符串）
import os

input_path = r"F:\repository\project\Own\etm-data-analysis\slider_setting\SliderSettingsOverview.csv"
output_path = r".\processed_output.csv"

if os.path.exists(input_path):
    print(f"输入文件存在: {input_path}")
    convert_semicolon_to_comma(input_path, output_path)
    print(f"已处理并输出到: {output_path}")
else:
    print(f"输入文件不存在: {input_path}")
