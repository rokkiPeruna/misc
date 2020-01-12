#!/usr/bin/python

import random
import sys
from timeit import default_timer as timer

DEF_ROUNDS = 1000000
MAX_INT = sys.maxsize 
GOLD_COIN = 1
SILVER_COIN = 0

boxes = (
  (GOLD_COIN, GOLD_COIN),
  (GOLD_COIN, SILVER_COIN),
  (SILVER_COIN, SILVER_COIN)
)

def run_rounds(rounds):
  hits = 0
  misses = 0
  i = 0
  print(f"Calculating {rounds} rounds..")

  start_time = timer()
  while i < rounds:
    picked_box = boxes[random.randint(0, MAX_INT) % len(boxes)]
    picked_coin = picked_box[random.randint(0, MAX_INT) % len(boxes[0])]

    if picked_box[picked_coin]:
      i += 1
      if picked_box[1 - picked_coin]:
        hits += 1
      else:
        misses += 1
  end_time = timer()

  print(f"Hits: {hits}")
  print(f"Misses: {misses}")
  print(f"Hit percent: {hits / rounds * 100}%")
  print(f"Miss percent: {misses / rounds * 100}%")
  print(f"Calculation time: {end_time - start_time} seconds")


if __name__ == "__main__":
  rounds = DEF_ROUNDS
  if len(sys.argv) > 1:
    rounds = int(sys.argv[1])
  run_rounds(rounds)
  sys.exit(0)
    