import pandas as pd
import os

# dataフォルダ内のCSVファイルのリストを取得
csv_files = [file for file in os.listdir('./data') if file.endswith('.csv')]

# 空のDataFrameを用意
combined_csv = pd.DataFrame()

# 各CSVファイルを読み込み、結合
for file in csv_files:
    df = pd.read_csv(f'./data/{file}')
    combined_csv = pd.concat([combined_csv, df], ignore_index=True)

combined_csv = combined_csv[~combined_csv['スコア'].str.contains('vs')]
combined_csv = combined_csv[~combined_csv['スコア'].str.contains('中止')]
combined_csv['スコア'] = combined_csv['スコア'].str.replace(r'\([^)]*\)', '', regex=True)
combined_csv.to_csv('./data/combined_csv.csv', index=False)
combined_csv[['Home Score', 'Away Score']] = combined_csv['スコア'].str.split('-', expand=True)

combined_csv['Home Score'] = combined_csv['Home Score'].astype(int)
combined_csv['Away Score'] = combined_csv['Away Score'].astype(int)
combined_csv['Winner'] = combined_csv.apply(lambda row: row['ホーム'] if row['Home Score'] > row['Away Score'] else (row['アウェイ'] if row['Home Score'] < row['Away Score'] else 'Draw'), axis=1)

combined_csv['試合日'] = combined_csv['試合日'].str.extract(r'(\d{2})/')[0].fillna(0).astype(int).astype(str)

combined_csv['入場者数'] = combined_csv['入場者数'].fillna("0").str.replace(',', '').astype(int)
combined_csv = combined_csv.drop('インターネット中継・TV放送', axis=1)
combined_csv.to_csv('./data/processed_csv.csv', index=False)
