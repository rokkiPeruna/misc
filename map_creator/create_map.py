#!/usr/bin/python3

import sys
import os
import argparse
import traceback
import math
import time
import copy
import shutil

from collections import OrderedDict

from perlin import Perlin1D, Perlin2D, Perlin3D


# Defaults
DEF_MAP_WIDTH  = 40
DEF_MAP_HEIGHT = 40
DEF_MAP_DEPTH  = 40
EMPTY          = " "
TERRAIN        = "X"

# Block types
BLOCK_TYPES = OrderedDict([
  ("VOID",  "0"),
  ("FLOOR", "1"),
  ("WALL",  "2"),
])


def map_values_1d(w, h, scaled_values):
  # Map values to 2D array
  final_map = [ [ EMPTY for _ in range(w) ] for _ in range(h) ]
  for x, y in scaled_values:
    if y < 0:
      y = 0
    elif y >= h:
      y = h
    try:
      final_map[y][x] = TERRAIN
    except Exception:
      print("Exception handling point: [{}, {}]".format(x, y))
      print(traceback.format_exc())

  return final_map


def create_map_1d(conf, perlin):
  data = []
  w, h = conf.width, conf.height

  for x in range(w):
    res = perlin.calc_octaves(x)
    if perlin.scale_r:
      res = perlin.scale_value(res)

  return map_values_1d(w, h, data)


def create_map_2d(conf, perlin):
  data = []
  w, h = conf.width, conf.height

  for y in range(h):
    line = []
    for x in range(w):
      res = perlin.calc_octaves((x, y))
      if perlin.scale_r:
        res = perlin.scale_value(res)
      line.append(res)
    data.append(line)

  return data


def create_map_3d(conf, perlin):
  return (1, 1, 1)


def format_map_data_to_str(map_data):
  return "\n".join(["".join([str(i) for i in line]) for line in map_data])


def save_map(conf, data):
  map_str = format_map_data_to_str(data)
  with open(os.path.join(conf.path, conf.map_name), "w") as newmap:
    newmap.write(map_str)


def print_map_info_table(conf):
  w, h, f, a = conf.width, conf.height, conf.frequency, conf.amplitude
  f_s, a_s = conf.freq_scale, conf.ampl_scale
  wall = " | "
  sep = "\n" + "-" * conf.width + "\r\n"
  info_table = f"FREQ: {f}{wall}FREQ SCALE: {f_s}{wall} AMPL: {a}{wall}AMPL SCALE: {a_s}{wall}WIDTH: {w}{wall}HEIGHT: {h}{sep}"
  sys.stdout.write(info_table)


def print_floor(width):
  sys.stdout.write("\n" + "=" * width + "\r")


def print_map_to_console(map_string):
  sys.stdout.write(map_string + "\r")


def clean_screen(height):
  sys.stdout.write("\033[{}A".format(height))


def interactive_mode_1d(conf, perlin):
  new_map = create_map_1d(conf, perlin)
  os.system("$(which clear)")
  next_x = conf.width + 1

  while True:
    try:
      # Calculate next point and apply it to the map
      y = perlin.calc_octaves(next_x)
      for c in new_map:
        c.pop(0)
        c.append(EMPTY)
      if y < 0:
        y = 0
      elif y >= conf.height:
        y = conf.height - 1
      new_map[int(y)][conf.width - 1] = TERRAIN
      map_str = format_map_data_to_str(new_map)

      # Print info table, map and move cursor to start position
      print_map_info_table(conf)
      print_map_to_console(map_str)
      print_floor(conf.width)
      clean_screen(conf.height + 1 + 1) # + roof + floor

      # Increment to next position and sleep to achieve desired framerate
      next_x += 1
      time.sleep(1.0 / conf.speed)

    except KeyboardInterrupt:
      break

    except Exception:
      print(traceback.format_exc())
      print("Points: ({}, {})".format(conf.width - 1, int(y)))
      break

  sys.stdout.write("\r")
  os.system("$(which clear)")


def interactive_mode_2d(conf, perlin):
  slice_nro = 0 # For wave effect only one line at a time needs to be calculated
  picture_tmpl = [[EMPTY for _ in range(conf.width)] for _ in range(conf.height)]
  os.system("$(which clear)")
  perlin.scale_r = (0, conf.height - 1)

  while True:
    try:
      picture = copy.deepcopy(picture_tmpl)
      # Calculate next picture
      for x in range(conf.width):
        x_val = x
        y_val = perlin.calc_octaves((x, slice_nro))
        if y_val < 0:
          y_val = 0
        elif y_val >= conf.height:
          y_val = conf.height - 1
        picture[y_val][x_val] = TERRAIN
      pic_str = format_map_data_to_str(picture)

      # Print info table, map and move cursor to start position
      print_map_info_table(conf)
      print_map_to_console(pic_str)
      print_floor(conf.width)
      clean_screen(conf.height + 1 + 1) # + roof + floor

      # Increment to next slice and sleep to achieve desired framerate
      slice_nro += 1
      time.sleep(1.0 / conf.speed)

    except KeyboardInterrupt:
      break

    except Exception:
      print(traceback.format_exc())
      print("Points: ({}, {})".format(x, y_val))
      break

  sys.stdout.write("\r")
  os.system("$(which clear)")


def main_default_mode(conf, perlin):
  if conf.dimension == 1:
    newmap = create_map_1d(conf, perlin)
  elif conf.dimension == 2:
    newmap = create_map_2d(conf, perlin)
  elif conf.dimension == 3:
    newmap = create_map_3d(conf, perlin)

  save_map(conf, newmap)


def parse_args():
  parser = argparse.ArgumentParser()

  # Map arguments
  parser.add_argument("-W", "--width", type=int, default=DEF_MAP_WIDTH, help="Desired map width")
  parser.add_argument("-H", "--height", type=int, default=DEF_MAP_HEIGHT, help="Desired map height")
  parser.add_argument("-D", "--depth", type=int, default=DEF_MAP_DEPTH, help="Desired map depth")
  parser.add_argument("-d", "--dimension", type=int, default=1, choices=[1, 2, 3], help="Map dimension: 1D, 2D or 3D")

  # Perlin arguments
  parser.add_argument("-a", "--amplitude", type=float, default=1.0, help="Initial amplitude")
  parser.add_argument("-f", "--frequency", type=float, default=300.0, help="Initial frequency")
  parser.add_argument("-o", "--octaves", type=int, default=4, help="Number of octaves per point")
  parser.add_argument("-A", "--ampl_scale", type=float, default=1.0, help="Scales the amplitude")
  parser.add_argument("-F", "--freq_scale", type=float, default=1.0, help="Scales the frequency")

  # Program arguments
  parser.add_argument("-N", "--map_name", type=str, default="newmap", help="Map file name")
  parser.add_argument("-P", "--path", type=str, default=os.getcwd(), help="Path where to save the map file")
  parser.add_argument("-S", "--speed", type=float, default=3, help="Update speed (frames per second) when on interactive mode")
  parser.add_argument("-R", "--mapping_range", type=str, help="The range in comma-separated list \
    in which the values are mapped, e.g. 0,20. On 1D, defaults to 0, <height> - 1. On 2D and 3D, defaults to 0,255")
  parser.add_argument("-I", "--interactive", default=0, action="count", help="Interactive mode for shell. \
    Width and height are determined by the console size")

  args = parser.parse_args()

  # Additional parsing
  if args.mapping_range:
    print(args.mapping_range)
    args.mapping_range = [int(r) for r in args.mapping_range.split(",")[0:2]]
  if not args.mapping_range:
    if args.dimension == 1:
      args.mapping_range = (0, args.height - 1)
    elif args.dimension in (2, 3):
      args.mapping_range = (0, 255)

  if args.interactive: # Use console size for width and height
    w, h = shutil.get_terminal_size((DEF_MAP_WIDTH, DEF_MAP_HEIGHT))
    args.width = w
    args.height = h - 3 # 3 == info table + floor

  return args


if __name__ == "__main__":
  try:
    conf = parse_args()
    perlin_args = [
      conf.amplitude,
      conf.ampl_scale,
      conf.frequency,
      conf.freq_scale,
      conf.octaves,
      conf.mapping_range,
    ]

    if conf.dimension == 1:
      perlin = Perlin1D(*perlin_args)
    elif conf.dimension == 2:
      perlin = Perlin2D(*perlin_args)
    elif conf.dimension == 3:
      perlin = Perlin3D(*perlin_args)

    if conf.interactive:
      if conf.dimension == 1:
        interactive_mode_1d(conf, perlin)
      elif conf.dimension == 2:
        interactive_mode_2d(conf, perlin)
      elif conf.dimension == 3:
        pass
    else:
      main_default_mode(conf, perlin)
  except Exception as ex:
    print(traceback.format_exc())
    sys.exit(1)

  sys.exit(0)
