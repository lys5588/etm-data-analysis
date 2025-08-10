import os
import csv
import argparse
import sys
from pathlib import Path
from collections import defaultdict


def traverse_folder_to_csv(folder_path, output_csv_path):
    """
    遍历文件夹结构，将文件组织信息保存到CSV文件中
    
    Args:
        folder_path (str): 要遍历的文件夹路径
        output_csv_path (str): 输出CSV文件路径
    """
    # 存储文件夹结构和文件信息
    folder_structure = defaultdict(list)
    max_depth = 0
    
    # 遍历文件夹
    for root, dirs, files in os.walk(folder_path):
        # 计算当前路径的深度
        rel_path = os.path.relpath(root, folder_path)
        if rel_path == '.':
            path_parts = []
        else:
            path_parts = rel_path.split(os.sep)
        
        current_depth = len(path_parts)
        max_depth = max(max_depth, current_depth)
        
        # 如果当前文件夹包含文件（叶文件夹）
        if files:
            # 获取文件名（不包含扩展名）
            file_names = [os.path.splitext(f)[0] for f in files if os.path.isfile(os.path.join(root, f))]
            file_names.sort()  # 按名称排序
            
            # 构建完整路径信息：从根文件夹到当前文件夹
            if path_parts:
                full_path = [os.path.basename(folder_path)] + path_parts
            else:
                full_path = [os.path.basename(folder_path)]
            
            # 存储路径和文件信息
            folder_structure[tuple(full_path)] = file_names
    
    # 写入CSV文件
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # 第一行：文件夹深度
        writer.writerow(['folder_depth', max_depth + 1])  # +1 因为包含根文件夹
        
        # 准备数据行
        all_paths = list(folder_structure.keys())
        if not all_paths:
            return
        
        # 计算最大列数（最长路径长度 + 最多文件数）
        max_path_length = max(len(path) for path in all_paths)
        max_files = max(len(files) for files in folder_structure.values())
        
        # 构建数据矩阵
        data_matrix = []
        
        # 对于每个叶文件夹
        for path_tuple in sorted(all_paths):
            files = folder_structure[path_tuple]
            
            # 创建列数据
            column_data = []
            
            # 添加路径信息（从根到叶文件夹）
            for i in range(max_path_length):
                if i < len(path_tuple):
                    column_data.append(path_tuple[i])
                else:
                    column_data.append('')
            
            # 添加文件名
            for file_name in files:
                column_data.append(file_name)
            
            data_matrix.append(column_data)
        
        # 转置矩阵以便按行写入
        if data_matrix:
            max_rows = max(len(col) for col in data_matrix)
            transposed = []
            for i in range(max_rows):
                row = []
                for col in data_matrix:
                    if i < len(col):
                        row.append(col[i])
                    else:
                        row.append('')
                transposed.append(row)
            
            # 写入所有行
            for row in transposed:
                writer.writerow(row)
    
    print(f"文件夹结构已保存到: {output_csv_path}")
    print(f"最大文件夹深度: {max_depth + 1}")
    print(f"找到 {len(all_paths)} 个叶文件夹")


def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        description="文件夹结构分析工具 - 遍历文件夹并生成CSV结构文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python generate_query.py /path/to/folder
  python generate_query.py /path/to/folder -o output.csv
  python generate_query.py /path/to/folder --output /path/to/output.csv
        """
    )
    
    parser.add_argument(
        'folder_path',
        help='要分析的文件夹路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出CSV文件路径（可包含文件名），默认为当前目录下的"文件夹名_structure.csv"'
    )
    
    return parser.parse_args()


def get_output_path(folder_path, output_arg):
    """
    根据输入参数确定输出文件路径
    
    Args:
        folder_path (str): 输入文件夹路径
        output_arg (str): 用户指定的输出参数
    
    Returns:
        str: 最终的输出文件路径
    """
    if output_arg:
        # 如果用户指定了输出路径
        if os.path.isdir(output_arg):
            # 如果指定的是目录，在该目录下生成默认文件名
            folder_name = os.path.basename(folder_path.rstrip(os.sep))
            return os.path.join(output_arg, f"{folder_name}_structure.csv")
        else:
            # 如果指定的是文件路径，直接使用
            return output_arg
    else:
        # 如果没有指定输出路径，使用默认文件名
        folder_name = os.path.basename(folder_path.rstrip(os.sep))
        return f"{folder_name}_structure.csv"


def main():
    """
    主函数，处理命令行参数并执行文件夹分析
    """
    try:
        args = parse_arguments()
        
        # 验证输入文件夹路径
        if not os.path.exists(args.folder_path):
            print(f"错误：文件夹路径不存在: {args.folder_path}", file=sys.stderr)
            sys.exit(1)
            
        if not os.path.isdir(args.folder_path):
            print(f"错误：输入的路径不是文件夹: {args.folder_path}", file=sys.stderr)
            sys.exit(1)
        
        # 确定输出文件路径
        output_csv_path = get_output_path(args.folder_path, args.output)
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_csv_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                print(f"创建输出目录: {output_dir}")
            except Exception as e:
                print(f"错误：无法创建输出目录 {output_dir}: {str(e)}", file=sys.stderr)
                sys.exit(1)
        
        # 执行文件夹分析
        print(f"开始分析文件夹: {args.folder_path}")
        traverse_folder_to_csv(args.folder_path, output_csv_path)
        print(f"分析完成！结果保存在: {os.path.abspath(output_csv_path)}")
        
    except KeyboardInterrupt:
        print("\n操作被用户中断", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误：{str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
