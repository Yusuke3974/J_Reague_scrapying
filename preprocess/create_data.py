import pandas as pd
import os
import re
from sklearn.preprocessing import LabelEncoder

#　学習データ作成
df = pd.read_csv('./data/preprocess/processed_csv.csv')
df = df.drop(["K/O時刻","Home Score","Away Score","date_time"], axis=1)


label_encoder =LabelEncoder()
df['Winner'] = label_encoder.fit_transform(df['Winner'])
df['Winner'].to_csv('./data/xy/winner.csv', index=False, header=True)

df = df.drop(["Winner"], axis=1)

predict_df = pd.read_csv('./data/predict/processed_csv.csv')
goals_df = pd.read_csv('./data/attach/team_goals.csv')
win_rate_df = pd.read_csv('./data/attach/win_rate.csv')
home_win_rate_df = pd.read_csv('./data/attach/home_win_rate.csv')

df = pd.concat([df, predict_df], axis=0)

df = pd.merge(df, home_win_rate_df, left_on='ホーム',right_on="チーム", how='left')
df = pd.merge(df, goals_df, left_on='ホーム',right_on="チーム", how='left')
df = pd.merge(df, goals_df, left_on='アウェイ',right_on="チーム", how='left')

df = df.drop(["チーム","チーム_x","チーム_y"], axis=1)

df = pd.merge(df, win_rate_df, left_on='ホーム',right_on="チーム", how='left')
df = pd.merge(df, win_rate_df, left_on='アウェイ',right_on="チーム", how='left')

df = df.drop(["チーム_x","チーム_y"], axis=1)


object_cols = ["ホーム","アウェイ","スタジアム"]
encoded_df = pd.get_dummies(df, columns=object_cols)

encoded_df = encoded_df.drop(["スコア"], axis=1)

traing_df = encoded_df[:len(df)-len(predict_df)]
predict_df = encoded_df[len(df)-len(predict_df):]

traing_df.to_csv('./data/preprocess/traing_df.csv', index=False)
predict_df.to_csv('./data/preprocess/predict_df.csv', index=False)