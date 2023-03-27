import pandas as pd

def from_excel_to_csv(excel_file_path, csv_file_path):
    read_file = pd.read_excel (excel_file_path)
    read_file.to_csv(csv_file_path, index=False)
# from_excel_to_csv("test.xlsx", "results.csv")

df = pd.read_csv('results.csv')
print(df["Price_close"][0])
# for index, row in df.iterrows():
#     print(index)
#     print(row.values)