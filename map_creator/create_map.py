#!/usr/bin/python3

import sys
import os
import argparse
import traceback
import random
import math
import time

from collections import OrderedDict


# Defaults
DEF_MAP_WIDTH  = 60
DEF_MAP_HEIGHT = 40
EMPTY          = " "
TERRAIN        = "X"

# Block types
BLOCK_TYPES = OrderedDict([
  ("VOID",  "0"),
  ("FLOOR", "1"),
  ("WALL",  "2"),
])


# https://flafla2.github.io/2014/08/09/perlinnoise.html
# https://gpfault.net/posts/perlin-noise.txt.html
# Perlin defaults
PERMUTATION_SOURCE = [
  33, 215, 184, 104, 125, 206, 187, 63, 67, 230, 46, 59, 195, 97, 6, 18, 137, 164, 226, 112,
  213, 185, 73, 114, 127, 197, 194, 45, 26, 22, 140, 37, 69, 36, 141, 64, 48, 56, 131, 239,
  217, 62, 91, 57, 199, 53, 44, 88, 42, 117, 0, 210, 249, 181, 182, 115, 94, 78, 54, 119,
  214, 139, 251, 50, 207, 121, 89, 55, 252, 103, 100, 113, 169, 219, 9, 177, 10, 74, 77, 82, 3,
  255, 93, 106, 38, 116, 135, 34, 39, 58, 1, 170, 147, 198, 167, 254, 41, 129, 253, 144, 81,
  161, 229, 52, 240, 95, 163, 128, 40, 51, 23, 236, 153, 201, 179, 233, 92, 191, 60, 160, 154,
  188, 243, 175, 124, 143, 130, 227, 25, 158, 32, 237, 156, 80, 162, 155, 65, 189, 14,
  12, 145, 86, 149, 223, 165, 24, 75, 126, 176, 183, 166, 108, 244, 208, 142, 70, 4, 68,
  133, 171, 28, 228, 247, 235, 83, 98, 84, 146, 29, 205, 61, 101, 134, 212, 17, 11, 209, 35, 159, 47,
  7, 43, 99, 5, 102, 168, 202, 30, 150, 2, 15, 136, 248, 120, 231, 21, 132, 152, 90, 172, 232, 238,
  118, 105, 49, 157, 13, 200, 242, 180, 224, 111, 203, 186, 31, 96, 192, 222, 122, 173, 174, 123,
  234, 110, 16, 218, 193, 151, 178, 76, 27, 216, 245, 190, 79, 87, 8, 20, 225, 204, 196, 107, 148,
  220, 72, 19, 250, 211, 109, 71, 66, 138, 85, 241, 246, 221
]
PERMUTATED_LIST = [i % 256 for i in range(512)]
RANDOM = [i for i in range(256)]
random.shuffle(RANDOM)


class PerlinBase(object):
  def __init__(self, amplitude : float, ampl_scale : float, frequency : float, freq_scale: float, octaves : int):
    self.rand_ord_0_to_255 = [ i for i in range(256) ]
    random.shuffle(self.rand_ord_0_to_255)

    # Configurables
    self.ampl = conf.amplitude
    self.ampl_scale = conf.ampl_scale
    self.freq = conf.frequency
    self.freq_scale = conf.freq_scale
    self.octaves = conf.octaves


  def calc_fade(self, point : float):
    return point * point * point * (point*(point*6.0 - 15.0) + 10.0)

  def calc_gradient(self, point : float):
    pass

  def calc_noise(self, point : float):
    pass


class Perlin1D(PerlinBase):
  def __init__(self, amplitude : float, ampl_scale : float, frequency : float, freq_scale : float, octaves : int):
    super().__init__(amplitude, ampl_scale, frequency, freq_scale, octaves)

  def calc_gradient(self, point):
    point = PERMUTATED_LIST[int(point) & 0xff]

    return -1.0 if (RANDOM[point] / 256.0) < 0.5 else 1.0


  def calc_lerp(self, point : float):
    p0 = math.floor(point)
    p1 = p0 + 1.0

    faded = self.calc_fade(point - p0)

    g0 = self.calc_gradient(p0)
    g1 = self.calc_gradient(p1)

    return (1.0 - faded) * g0 * (point - p0) + faded * g1 * (point - p1)


  def calc_noise(self, point):
    initial_freg = 300.0
    initial_ampl = 1.0
    amplitude_scale = conf.ampl_scale
    frequency_scale = conf.freq_scale
    res = 0.0

    for i in range(conf.octaves):
      freq = (initial_freg / 2**i) * frequency_scale
      ampl = (initial_ampl / 2**i) * amplitude_scale
      res += self.calc_lerp(point * (1.0 / freq)) * ampl

    return res


class Perlin2D(PerlinBase):
  def __init__(self, amplitude : float, ampl_scale : float, frequency : float, freq_scale : float, octaves : int):
    super().__init__(amplitude, ampl_scale, frequency, freq_scale, octaves)



class Perlin3D(PerlinBase):
  def __init__(self, amplitude : float, ampl_scale : float, frequency : float, freq_scale : float, octaves : int):
    super().__init__(amplitude, ampl_scale, frequency, freq_scale, octaves)


def scale_values(w, h, x, y):
  norm = lambda v: (v + 1.0) / 2.0 # [-1, 1] -> [0, 1]
  return x, math.floor(norm(y) * h)


def map_values(w, h, scaled_values):
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
  scaled_y_values = [] # (x, scaled y)

  # For every x-axis value, calculate y-value [-1.0, 1.0]
  for x in range(w):
    data.append(perlin.calc_noise(x))

  # Scale values according to map height
  for x, y in enumerate(data):
    scaled_y_values.append(scale_values(w, h, x, y))

  final_map = map_values(w, h, scaled_y_values)

  return final_map


def format_map_data_to_str(map_data):
  return "\n".join(["".join([str(i) for i in line]) for line in map_data])


def save_map(conf, data):
  map_str = format_map_data_to_str(data)
  with open(os.path.join(conf.path, conf.map_name), "w") as newmap:
    newmap.write(map_str)


def main_interactive_mode(conf, perlin):
  # Calculate and print initial map
  new_map = create_map_1d(conf, perlin)
  print(format_map_data_to_str(new_map))

  next_x = conf.width + 1
  carry_on = True
  while carry_on:
    try:
      os.system("$(which clear)")
      next_y = perlin.calc_noise(next_x)

      for c in new_map:
        c.pop(0)
        c.append(EMPTY)

      y = scale_values(0, conf.height, next_x, next_y)[1] # Only y-value needed
      if y < 0:
        y = 0
      elif y >= conf.height:
        y = conf.height - 1
      new_map[y][conf.width - 1] = TERRAIN

      map_str = format_map_data_to_str(new_map)

      print(map_str)
      next_x += 1
      time.sleep(1.0 / conf.speed)

    except KeyboardInterrupt:
      carry_on = False
    except Exception:
      print(traceback.format_exc())
      carry_on = False


def main_default_mode(conf, perlin):
  newmap = create_map_1d(conf, perlin)
  save_map(conf, newmap)


def parse_args():
  parser = argparse.ArgumentParser()

  # Map arguments
  parser.add_argument("-W", "--width", type=int, default=DEF_MAP_WIDTH, help="Desired map width")
  parser.add_argument("-H", "--height", type=int, default=DEF_MAP_HEIGHT, help="Desired map height")
  parser.add_argument("-D", "--dimension", type=int, default=1, help="Map dimension: 1D, 2D or 3D")

  # Perlin arguments
  parser.add_argument("-a", "--amplitude", type=float, default=1.0, help="Initial amplitude")
  parser.add_argument("-f", "--frequency", type=float, default=300.0, help="Initial frequency")
  parser.add_argument("-o", "--octaves", type=int, default=4, help="Number of octaves per point")
  parser.add_argument("-A", "--ampl_scale", type=float, default=1.0, help="Scales the amplitude")
  parser.add_argument("-F", "--freq_scale", type=float, default=1.0, help="Scales the frequency")

  # Program arguments
  parser.add_argument("-N", "--map_name", type=str, default="newmap", help="Map file name")
  parser.add_argument("-P", "--path", type=str, default=os.getcwd(), help="Path where to save the map file")
  parser.add_argument("-I", "--interactive", default=0, action="count", help="Interactive mode for shell")
  parser.add_argument("-S", "--speed", type=float, default=3, help="Update speed (frames per second) when on interactive mode")

  return parser.parse_args()


if __name__ == "__main__":
  try:
    conf = parse_args()

    perlin_args = [
      conf.amplitude,
      conf.ampl_scale,
      conf.frequency,
      conf.freq_scale,
      conf.octaves
    ]

    if conf.dimension == 1:
      perlin = Perlin1D(*perlin_args)
    if conf.dimension == 2:
      perlin = Perlin2D(*perlin_args)
    if conf.dimension == 3:
      perlin = Perlin3D(*perlin_args)

    if conf.interactive:
      main_interactive_mode(conf, perlin)
    else:
      main_default_mode(conf, perlin)
  except Exception as ex:
    print(traceback.format_exc())
    sys.exit(1)

  sys.exit(0)
