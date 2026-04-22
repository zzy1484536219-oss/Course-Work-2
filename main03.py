import pandas as pd


def get_hierarchy(desc):
    """终极版疾病自动分类引擎，保证每一层都有丰富的切分"""
    desc = str(desc).lower()

    # --- 01. 肿瘤类 ---
    if 'neoplasms' in desc or 'cancer' in desc:
        if any(x in desc for x in
               ['digestive', 'stomach', 'colon', 'liver']): return "01. Neoplasms", "1.1 Digestive Cancers"
        if any(x in desc for x in
               ['respiratory', 'lung', 'intrathoracic']): return "01. Neoplasms", "1.2 Respiratory Cancers"
        if any(x in desc for x in
               ['breast', 'genital', 'urinary']): return "01. Neoplasms", "1.3 Urogenital & Breast Cancers"
        return "01. Neoplasms", "1.4 Other Neoplasms"

    # --- 02. 循环与呼吸系统 ---
    if any(x in desc for x in ['circulatory', 'heart', 'ischemic', 'cerebrovascular', 'veins']):
        return "02. Cardio-Respiratory", "2.1 Heart & Vascular Diseases"
    if any(x in desc for x in ['respiratory', 'lung', 'influenza', 'pneumonia', 'tonsils']):
        return "02. Cardio-Respiratory", "2.2 Airway & Lung Diseases"

    # --- 03. 消化与内脏 ---
    if any(x in desc for x in ['digestive', 'appendix', 'hernia', 'intestine', 'gallbladder']):
        return "03. Internal Organs", "3.1 Gastrointestinal System"
    if any(x in desc for x in ['genitourinary', 'kidney', 'urinary', 'renal', 'pelvic']):
        return "03. Internal Organs", "3.2 Urinary & Renal System"
    if any(x in desc for x in ['endocrine', 'metabolic', 'diabetes', 'thyroid']):
        return "03. Internal Organs", "3.3 Endocrine & Metabolic"

    # --- 04. 神经、感官与骨骼 ---
    if any(x in desc for x in ['nervous', 'brain', 'eye', 'ear', 'vision']):
        return "04. Neuro & Senses", "4.1 Nervous & Senses"
    if any(x in desc for x in ['musculoskeletal', 'bone', 'joint', 'arthrosis', 'tissue', 'skin']):
        return "04. Neuro & Senses", "4.2 Musculoskeletal & Skin"

    # --- 05. 传染与母婴 ---
    if any(x in desc for x in ['infectious', 'parasitic', 'virus', 'bacterial']):
        return "05. Infection & Maternal", "5.1 Infectious Diseases"
    if any(x in desc for x in ['pregnancy', 'childbirth', 'perinatal', 'congenital', 'malformations']):
        return "05. Infection & Maternal", "5.2 Maternal & Neonatal"

    # --- 06. 损伤与症状 ---
    if any(x in desc for x in ['injury', 'fracture', 'poisoning', 'burn', 'trauma', 'external']):
        return "06. Injury & Symptoms", "6.1 Trauma & Injury"
    if any(x in desc for x in ['symptoms', 'signs', 'abnormal', 'clinical']):
        return "06. Injury & Symptoms", "6.2 Unknown Symptoms"

    # --- 07. Z代码 (健康接触) ---
    if "factors influencing health" in desc or desc.startswith('z'):
        return "07. Health Factors (Z-Codes)", "7.1 Health Services Contact"

    return "08. Others", "8.1 Miscellaneous"


# ==========================================
# 数据处理执行区
# ==========================================
# 读取你现有的合并数据
df = pd.read_csv('merged_Primary_Summary_2012_to_2024.csv')

# 1. 彻底清除空行和 Total 垃圾行
df = df.dropna(subset=['Record_Year'])
for col in df.columns[:5]:
    df = df[df[col].astype(str).str.strip().str.lower() != 'total']

# 2. 定位疾病描述列（通常是 Unnamed: 1，如果不是，取第3列）
desc_col = 'Unnamed: 1' if 'Unnamed: 1' in df.columns else df.columns[2]

# 3. 生成层次结构
hier_data = df[desc_col].apply(get_hierarchy)
df['Level_1_Category'] = [x[0] for x in hier_data]
df['Level_2_SubCategory'] = [x[1] for x in hier_data]
df['Disease_Description'] = df[desc_col]

# 4. 导出为终极版文件
output_filename = 'HES_Treemap_Ultimate.csv'
df.to_csv(output_filename, index=False, encoding='utf-8-sig')
print(f"处理完毕！请在 Tableau 中连接文件：{output_filename}")