#!/usr/bin/python3

import sys
import os
import argparse
import traceback
import random

from collections import OrderedDict


# Defaults
DEF_MAP_WIDTH  = 30
DEF_MAP_HEIGHT = 30
MAX_INT        = sys.maxsize

# Block types
BLOCK_TYPES = OrderedDict([
  ("VOID",  "0"),
  ("FLOOR", "1"),
  ("WALL",  "2"),
])


def _parse_args():
  parser = argparse.ArgumentParser()

  parser.add_argument("-W", "--width", type=int, default=DEF_MAP_WIDTH, help="Desired map width")
  parser.add_argument("-H", "--height", type=int, default=DEF_MAP_HEIGHT, help="Desired map height")
  parser.add_argument("-N", "--map_name", type=str, default="newmap", help="Map file name")
  parser.add_argument("-P", "--path", type=str, default=os.getcwd(), help="Path where to save the map file")

  return parser.parse_args()


def _create_map(conf):
  data = []
  blocks = list(BLOCK_TYPES.items())
  for h in range(0, conf.height):
    line = []
    for w in range(0, conf.width):
      b = blocks[random.randint(0, MAX_INT) % len(BLOCK_TYPES)]
      line.append(b[1])
    data.append(line)

  return data



def _save_map(conf, data):
  with open(os.path.join(conf.path, conf.map_name), "w") as newmap:
    for line in data:
      newmap.write(",".join(line) + "\n")


if __name__ == "__main__":
  try:
    conf = _parse_args()
    newmap = _create_map(conf)
    _save_map(conf, newmap)
  except Exception as ex:
    print(traceback.format_exc())
    sys.exit(1)

  sys.exit(0)
