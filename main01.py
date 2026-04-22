import pandas as pd
from pathlib import Path
import re


def clean_col_name(c):
    """专门应对2023年后列名大改版的清洗函数"""
    if not isinstance(c, str):
        return c

    # 处理几个被官方完全重命名的特殊列
    c_strip = c.strip()
    if c_strip == 'Finished Admission Episodes': return 'Admissions'
    if c_strip == 'Other (FAE)': return 'Other Admission Method'
    if c_strip == 'Emergency \n(FAE).1': return 'Emergency.1'
    if c_strip == 'Elective\n(FAE)': return 'Elective'
    if c_strip == 'Other\n(FAE)': return 'Other'

    # 通用处理：干掉换行符，并用正则删掉 (FCE), (FAE), (Days), (Years) 等碍事的后缀
    c = c.replace('\n', ' ')
    c = re.sub(r'\s*\((FCE|FAE|Days|Years)\)', '', c, flags=re.IGNORECASE)

    return c.strip()


def merge_specific_sheet_data(data_folder_path, output_folder_path):
    data_dir = Path(data_folder_path)
    output_dir = Path(output_folder_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_years_data = []
    print(f"开始扫描目录: {data_dir.absolute()}\n" + "-" * 40)

    for file_path in data_dir.glob("*.xlsx"):
        # 提取完整的财年格式，例如 "2023-24"
        match = re.search(r'(20\d{2}-\d{2})', file_path.name)

        if match:
            year_label = match.group(1)
            print(f"\n正在处理: {file_path.name} -> 归属年份: {year_label}")

            try:
                xl = pd.ExcelFile(file_path)
                available_sheets = xl.sheet_names

                target_sheet = None
                for sheet in available_sheets:
                    sheet_lower = sheet.lower()
                    if 'primary' in sheet_lower and 'summary' in sheet_lower:
                        target_sheet = sheet
                        break

                if target_sheet:
                    print(f"  - 命中目标页面: '{target_sheet}'")

                    # 1. 寻找真实表头
                    df_preview = xl.parse(sheet_name=target_sheet, header=None, nrows=30)
                    real_header_idx = 0
                    for idx, row in df_preview.iterrows():
                        if row.notna().sum() > 3:
                            real_header_idx = idx
                            print(f"    * 探测到真实表头位于第 {real_header_idx + 1} 行")
                            break

                    # 2. 读取数据
                    df = xl.parse(sheet_name=target_sheet, header=real_header_idx)

                    # 3. 统一列名
                    df.columns = [clean_col_name(col) for col in df.columns]

                    # 4. 剔除底部全空行和没有核心数据的版权注释
                    if 'Finished consultant episodes' in df.columns:
                        df = df.dropna(subset=['Finished consultant episodes'])

                    # 5. 【终极精准查杀 Total】：扫描前3列，凡是单元格内容等于 "Total" 的，全部踢掉！
                    # 无论它出现在开头还是结尾，都无处遁形
                    for col in df.columns[:3]:
                        # 转换小写并去除首尾空格，进行绝对比对
                        mask = df[col].astype(str).str.strip().str.lower() == 'total'
                        df = df[~mask]

                    # 6. 打上完整的财年标签
                    df['Record_Year'] = year_label
                    print(f"  - 提取纯净数据形状: {df.shape[0]}行, {df.shape[1]}列")

                    all_years_data.append(df)
                else:
                    print(f"  [跳过] 未找到包含 'Primary' 和 'Summary' 的页面。")

            except Exception as e:
                print(f"  [错误] 读取文件 {file_path.name} 时失败: {e}")

    # --- 合并环节 ---
    if all_years_data:
        print("\n" + "-" * 40)
        print("所有指定页面读取完毕，正在执行纵向合并...")

        # 纵向合并
        combined_df = pd.concat(all_years_data, ignore_index=True)

        # 【拦截底部残缺的幽灵空行】
        # 如果合并后的数据有 Record_Year 为空的行（如之前发现的末尾那一行），直接剔除
        combined_df = combined_df.dropna(subset=['Record_Year'])

        # 将年份列移动到第一列方便查看
        cols = combined_df.columns.tolist()
        if 'Record_Year' in cols:
            cols.insert(0, cols.pop(cols.index('Record_Year')))
            combined_df = combined_df[cols]

        print(f"合并成功！超级大表形状: {combined_df.shape[0]}行, {combined_df.shape[1]}列\n")

        output_csv = output_dir / 'merged_Primary_Summary_2012_to_2024.csv'
        combined_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"完美对齐的数据已成功保存至: {output_csv.absolute()}")

        return combined_df
    else:
        print("合并失败：未成功提取到任何数据。")
        return None


if __name__ == "__main__":
    MY_DATA_FOLDER = "."
    MY_OUTPUT_FOLDER = "./merged_output"
    final_dataframe = merge_specific_sheet_data(MY_DATA_FOLDER, MY_OUTPUT_FOLDER)