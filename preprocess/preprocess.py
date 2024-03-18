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

original_csv['日付'] = original_csv['試合日'].str.extract(r'(\d{2}/\d{2})')

# '年度'と'日付'を結合してdatetime型のデータを作成する
original_csv['date_time'] = pd.to_datetime(original_csv['年度'].astype(str) + '/' + original_csv['日付'], format='%Y/%m/%d')

# 不要なカラムを削除する
original_csv = original_csv.drop(['日付'], axis=1)

combined_csv = original_csv[~original_csv['スコア'].str.contains('vs')]
predict_csv = original_csv[original_csv['スコア'].str.contains('vs')]
predict_csv = predict_csv[~predict_csv['スコア'].str.contains('中止')]
predict_csv = predict_csv[predict_csv["年度"] == 2024]
predict_csv['試合日'] = predict_csv['試合日'].str.extract(r'(\d{2})/')[0].fillna(0).astype(int).astype(str)

predict_csv['K/O時刻_New'] = predict_csv['K/O時刻'].apply(lambda x: int(x.split(':')[0]) if x.strip() else None)
#predict_csv['入場者数'] = predict_csv['入場者数'].apply(lambda x: int(x.replace(',', '')) if x.strip() else None)
predict_csv = predict_csv.drop(["大会","K/O時刻","節",'インターネット中継・TV放送','入場者数',"date_time"], axis=1)
predict_csv.to_csv('./data/predict/processed_csv.csv', index=False)


combined_csv = combined_csv[~combined_csv['スコア'].str.contains('中止')]
#combined_csv = combined_csv[~combined_csv['試合日'].str.contains('未定')]

combined_csv['スコア'] = combined_csv['スコア'].str.replace(r'\([^)]*\)', '', regex=True)
#combined_csv.to_csv('./data/combined_csv.csv', index=False)
combined_csv[['Home Score', 'Away Score']] = combined_csv['スコア'].str.split('-', expand=True)

combined_csv['Home Score'] = combined_csv['Home Score'].astype(int)
combined_csv['Away Score'] = combined_csv['Away Score'].astype(int)
combined_csv['Winner'] = combined_csv.apply(lambda row: "ホームチーム" if row['Home Score'] > row['Away Score'] else ("アウェイチーム" if row['Home Score'] < row['Away Score'] else 'ドロー'), axis=1)

combined_csv['試合日'] = combined_csv['試合日'].str.extract(r'(\d{2})/')[0].fillna(0).astype(int).astype(str)

combined_csv['K/O時刻_New'] = combined_csv['K/O時刻'].apply(lambda x: int(x.split(':')[0]) if x.strip() else None)

#combined_csv['入場者数'] = combined_csv['入場者数'].fillna("0").str.replace(',', '').astype(int)
combined_csv = combined_csv.drop(['入場者数',"大会","節",'インターネット中継・TV放送'], axis=1)
combined_csv.to_csv('./data/preprocess/processed_csv.csv', index=False)


# 直近の勝率を計算する
# 直近3か月のデータを抽出する
recent_three_months_data = combined_csv[combined_csv['date_time'] >= pd.Timestamp.now() - pd.DateOffset(months=3)]

# ホームチームの勝利数をカウントする
home_wins = recent_three_months_data[recent_three_months_data['Winner'] == 'ホームチーム']['ホーム'].value_counts().reset_index()
home_wins.columns = ['チーム', '勝利数']

# アウェイチームの勝利数をカウントする
away_wins = recent_three_months_data[recent_three_months_data['Winner'] == 'アウェイチーム']['アウェイ'].value_counts().reset_index()
away_wins.columns = ['チーム', '勝利数']

# 各チームの試合数をカウントする
matches = pd.concat([recent_three_months_data['ホーム'].value_counts(), recent_three_months_data['アウェイ'].value_counts()], axis=1, keys=['ホーム試合数', 'アウェイ試合数']).fillna(0).astype(int)
matches['試合数'] = matches['ホーム試合数'] + matches['アウェイ試合数']

# 各チームの勝率を計算する
win_rate = pd.merge(home_wins, away_wins, on='チーム', how='outer').fillna(0)
win_rate['勝利数'] = win_rate['勝利数_x'] + win_rate['勝利数_y']
win_rate.drop(['勝利数_x', '勝利数_y'], axis=1, inplace=True)
win_rate = pd.merge(win_rate, matches, left_on='チーム', right_index=True, how='outer').fillna(0)
win_rate['勝率'] = win_rate['勝利数'] / win_rate['試合数']
# NaNを0に置き換える
win_rate.fillna(0, inplace=True)
win_rate = win_rate[['チーム', '勝率']]
win_rate.to_csv('./data/attach/win_rate.csv', index=False)
print("CSVファイルにデータを保存しました。")

# 直近3か月のデータを抽出する
recent_three_months_data = combined_csv[combined_csv['date_time'] >= pd.Timestamp.now() - pd.DateOffset(months=3)]

# チームごとに相手チームと勝敗の組み合わせをカウントする
matchup_counts = recent_three_months_data.groupby(['ホーム', 'アウェイ', 'Winner']).size().unstack(fill_value=0)

# 各相手チームごとの相性を計算する
total_matches = matchup_counts.sum(axis=1)
winning_matches = matchup_counts.loc[:, 'ホームチーム'] + matchup_counts.loc[:, 'アウェイチーム']
matchup_counts['Win Rate'] = winning_matches / total_matches
matchup_counts.to_csv('./data/attach/matchup_counts.csv')

# 直近3か月のデータを抽出する
recent_three_months_data = combined_csv[combined_csv['date_time'] >= pd.Timestamp.now() - pd.DateOffset(months=3)]

# チームごとにホームでの勝利数と試合数をカウントする
home_wins = recent_three_months_data[recent_three_months_data['Winner'] == 'ホームチーム']['ホーム'].value_counts().reset_index()
home_wins.columns = ['チーム', 'ホーム勝利数']
home_matches = recent_three_months_data['ホーム'].value_counts().reset_index()
home_matches.columns = ['チーム', 'ホーム試合数']

# ホーム勝率を計算する
home_win_rate = pd.merge(home_wins, home_matches, on='チーム', how='outer').fillna(0)
home_win_rate['ホーム勝率'] = home_win_rate['ホーム勝利数'] / home_win_rate['ホーム試合数']
home_win_rate = home_win_rate.drop(['ホーム勝利数', 'ホーム試合数'], axis=1)
home_win_rate.to_csv('./data/attach/home_win_rate.csv', index=False)
print("CSVファイルにデータを保存しました。")


# 直近3か月のデータを抽出する
recent_three_months_data = combined_csv[combined_csv['date_time'] >= pd.Timestamp.now() - pd.DateOffset(months=3)]

# ホームチームごとのホームでのゴール数を合計する
home_goals = recent_three_months_data.groupby('ホーム')['Home Score'].sum().reset_index()
home_goals.columns = ['チーム', 'ホームでのゴール数']

# アウェイチームごとのアウェイでのゴール数を合計する
away_goals = recent_three_months_data.groupby('アウェイ')['Away Score'].sum().reset_index()
away_goals.columns = ['チーム', 'アウェイでのゴール数']

# 各チームの直近3か月の合計ゴール数を計算する
total_goals = pd.merge(home_goals, away_goals, on='チーム', how='outer').fillna(0)
total_goals['合計ゴール数'] = total_goals['ホームでのゴール数'] + total_goals['アウェイでのゴール数']
total_goals = total_goals.drop(['ホームでのゴール数', 'アウェイでのゴール数'], axis=1)
total_goals.to_csv('./data/attach/team_goals.csv', index=False)
print("CSVファイルにデータを保存しました。")