#!/usr/bin/python

import random
import sys

max_int = sys.maxsize 
rounds = 1000000

gold_coin = 1
silver_coin = 0
hits = 0
misses = 0

boxes = (
  (gold_coin, gold_coin),
  (gold_coin, silver_coin),
  (silver_coin, silver_coin)
)

i = 0
while i < rounds:
  picked_box = boxes[random.randint(0, max_int) % len(boxes)]
  picked_coin = picked_box[random.randint(0, max_int) % len(boxes[0])]

  if picked_box[picked_coin]:
    i += 1
    if picked_box[1 - picked_coin]:
      hits += 1
    else:
      misses += 1

print(f"{rounds} rounds calculated")
print(f"Hits: {hits}")
print(f"Misses: {misses}")
print(f"Hit percent: {hits / rounds * 100}%")
print(f"Miss percent: {misses / rounds * 100}%")
