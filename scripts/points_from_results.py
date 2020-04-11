import csv
import numpy as np

points_label = "Points"
lineup_label = "Lineup"
players = set()
num_lineups = 0

with open('outcome.csv', 'rb') as csvfile:
  rows = csv.reader(csvfile)
  next(rows, None)  # skip the headers
  for row in rows:
    names = [name.strip() for name in row[5].replace('(G)','').split(',')]
    for name in names:
      players.add(name)
    num_lineups += 1

player_list = list(players)
player_list.sort() #inline sort
player_count = len(player_list)

player_coefficients = []
lineup_points = []
with open('outcome.csv', 'rb') as csvfile:
  rows = csv.reader(csvfile)
  headers = rows.next()
  points_index = headers.index(points_label)
  lineup_index = headers.index(lineup_label)
  for row in rows:
    points = float(row[points_index])
    lineup_points.append(points)
    names = [name.strip() for name in row[lineup_index].replace('(G)','').split(',')]
    lineup_players = [0] * player_count
    for name in names:
      lineup_players[player_list.index(name)] = 1
    player_coefficients.append(lineup_players)

coefficient_matrix = np.array(player_coefficients)
point_array = np.array(lineup_points).transpose()
solution = np.linalg.lstsq(coefficient_matrix, point_array)
player_points = list(solution[0])

player_hash = {}
for index, name, in enumerate(player_list):
  player_hash[name] = float(player_points[index])

values = []
for name, points in player_hash.items():
  values.append((name, points))

sorted_plays = sorted(values, key=lambda tup: tup[1], reverse=True)
for player in sorted_plays: 
  print player[0] + ': ' + str(player[1])
