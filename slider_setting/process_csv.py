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
        


# Example usage:
process_csv("/Users/liyunshan/Downloads/SliderSettingsOverview.csv")
