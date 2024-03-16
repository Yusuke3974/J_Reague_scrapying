import csv
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import os
import numpy as np
import time

ssl._create_default_https_context = ssl._create_unverified_context

# URLの指定

year_list = ["2024","2023","2022", "2021", "2020"]

dir = './data'
if not os.path.exists(dir):
  os.makedirs(dir)

for year in year_list:
  time.sleep(5)
  html = urlopen(f"https://data.j-league.or.jp/SFMS01/search?competition_years={year}&tv_relay_station_name=")
  bsObj = BeautifulSoup(html, "html.parser")

  # テーブルを指定
  table = bsObj.findAll("table", {"class":"table-base00 search-table"})[0]
  rows = table.findAll("tr")

  with open(f"./data/{year}_results.csv", "w", encoding='utf-8') as file:
      writer = csv.writer(file)
      for row in rows:
          csvRow = []
          for cell in row.findAll(['td', 'th']):
              csvRow.append(cell.get_text())
          writer.writerow(csvRow)