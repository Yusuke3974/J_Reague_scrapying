import pandas as pd
import os
import re

# dataフォルダ内のCSVファイルのリストを取得
csv_files = [file for file in os.listdir('./data') if file.endswith('.csv')]

# 空のDataFrameを用意
original_csv = pd.DataFrame()

# 各CSVファイルを読み込み、結合
for file in csv_files:
    df = pd.read_csv(f'./data/{file}')
    original_csv = pd.concat([original_csv, df], ignore_index=True)


# オブジェクト型のセルから改行文字とタブ文字を削除する関数を定義
def remove_tabs_and_newlines(cell_value):
    if isinstance(cell_value, str):
        return re.sub(r'[\r\t\n]', '', cell_value)
    else:
        return cell_value

# DataFrameの全てのセルに関数を適用して改行文字とタブ文字を削除する
original_csv = original_csv.map(remove_tabs_and_newlines)

original_csv = original_csv.fillna("0")

original_csv = original_csv.astype({'年度': 'int64', '大会': 'object', '節': 'object',
                                    '試合日': 'object', 'K/O時刻': 'object', 'ホーム': 'object',
                                    'スコア': 'object', 'アウェイ': 'object', 'スタジアム': 'object',
                                '入場者数': 'object', 'インターネット中継・TV放送': 'object'})


combined_csv = original_csv[~original_csv['スコア'].str.contains('vs')]
predict_csv = original_csv[original_csv['スコア'].str.contains('vs')]
predict_csv = predict_csv[~predict_csv['スコア'].str.contains('中止')]
predict_csv = predict_csv[predict_csv["年度"] == 2024]
predict_csv['試合日'] = predict_csv['試合日'].str.extract(r'(\d{2})/')[0].fillna(0).astype(int).astype(str)

predict_csv['K/O時刻_New'] = predict_csv['K/O時刻'].apply(lambda x: int(x.split(':')[0]) if x.strip() else None)
predict_csv['入場者数_new'] = predict_csv['入場者数'].apply(lambda x: int(x.replace(',', '')) if x.strip() else None)
predict_csv = predict_csv.drop(["大会","節",'インターネット中継・TV放送'], axis=1)
predict_csv.to_csv('./data/predict/processed_csv.csv', index=False)

#predict_csv = predict_csv[~predict_csv['試合日'].str.contains('未定')]


combined_csv = combined_csv[~combined_csv['スコア'].str.contains('中止')]
#combined_csv = combined_csv[~combined_csv['試合日'].str.contains('未定')]

combined_csv['スコア'] = combined_csv['スコア'].str.replace(r'\([^)]*\)', '', regex=True)
#combined_csv.to_csv('./data/combined_csv.csv', index=False)
combined_csv[['Home Score', 'Away Score']] = combined_csv['スコア'].str.split('-', expand=True)

combined_csv['Home Score'] = combined_csv['Home Score'].astype(int)
combined_csv['Away Score'] = combined_csv['Away Score'].astype(int)
combined_csv['Winner'] = combined_csv.apply(lambda row: "ホームチーム" if row['Home Score'] > row['Away Score'] else ("アウェイチーム" if row['Home Score'] < row['Away Score'] else 'Draw'), axis=1)

combined_csv['試合日'] = combined_csv['試合日'].str.extract(r'(\d{2})/')[0].fillna(0).astype(int).astype(str)

combined_csv['K/O時'] = combined_csv['K/O時刻'].str.split(':').str[0].astype(int)

combined_csv['入場者数'] = combined_csv['入場者数'].fillna("0").str.replace(',', '').astype(int)
combined_csv = combined_csv.drop(["大会","節",'インターネット中継・TV放送'], axis=1)
combined_csv.to_csv('./data/preprocess/processed_csv.csv', index=False)


# predict


