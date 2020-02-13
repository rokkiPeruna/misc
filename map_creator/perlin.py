
import random
import math

# https://flafla2.github.io/2014/08/09/perlinnoise.html
# https://gpfault.net/posts/perlin-noise.txt.html


# Perlin defaults
PERMUTATION_SOURCE = \
(31, 99, 136, 15, 174, 2, 75, 87, 89, 71, 207, 108, 28, 201, 162, 125, 127, 43,
238, 107, 242, 23, 228, 245, 102, 29, 91, 24, 140, 92, 175, 68, 246, 151, 145,
32, 214, 157, 132, 149, 78, 134, 116, 155, 112, 52, 208, 189, 212, 195, 8, 77,
167, 233, 251, 98, 158, 227, 239, 48, 97, 66, 252, 44, 12, 250, 50, 128, 181,
173, 72, 21, 34, 225, 186, 253, 60, 109, 40, 172, 147, 42, 46, 96, 22, 166, 110,
86, 94, 115, 3, 118, 138, 101, 221, 82, 56, 130, 153, 241, 188, 38, 4, 122, 236,
200, 7, 104, 53, 83, 88, 64, 142, 129, 123, 177, 203, 180, 193, 229, 18, 226,
39, 121, 25, 58, 192, 182, 160, 202, 248, 139, 41, 93, 111, 95, 120, 80, 240,
211, 14, 205, 20, 113, 137, 148, 232, 84, 36, 124, 163, 219, 183, 231, 5, 255,
254, 178, 209, 70, 224, 11, 213, 61, 35, 198, 59, 54, 49, 249, 16, 184, 199, 168,
45, 165, 216, 159, 206, 19, 222, 143, 152, 63, 74, 0, 73, 215, 33, 114, 223, 117,
100, 27, 69, 10, 141, 90, 190, 105, 187, 196, 126, 133, 51, 191, 169, 26, 17, 62,
161, 210, 154, 179, 194, 220, 218, 37, 204, 171, 6, 150, 235, 243, 217, 176, 76,
55, 135, 106, 146, 234, 144, 1, 119, 156, 30, 65, 85, 247, 103, 244, 230, 81, 197,
13, 131, 170, 67, 79, 9, 237, 164, 47, 185, 57, 190, 127, 14, 125, 169, 48, 97,
223, 22, 241, 148, 247, 146, 202, 209, 255, 2, 215, 155, 240, 52, 206, 186, 220,
181, 188, 21, 77, 132, 73, 88, 227, 83, 50, 226, 4, 69, 28, 238, 152, 170, 141,
252, 166, 74, 104, 60, 46, 177, 75, 171, 81, 245, 82, 114, 173, 119, 33, 210, 185,
103, 64, 17, 160, 151, 168, 232, 197, 26, 115, 130, 35, 18, 23, 244, 236, 149, 11,
165, 135, 7, 191, 192, 111, 57, 162, 246, 13, 129, 41, 112, 51, 156, 108, 1, 55,
20, 140, 47, 95, 0, 219, 71, 29, 234, 139, 70, 250, 124, 212, 19, 157, 225, 126,
161, 32, 193, 243, 6, 178, 87, 201, 228, 131, 3, 208, 12, 43, 85, 175, 248, 231,
145, 204, 229, 53, 90, 8, 195, 16, 113, 235, 36, 143, 56, 107, 176, 72, 39, 205,
237, 38, 24, 142, 159, 233, 106, 180, 182, 230, 137, 99, 199, 189, 214, 183, 49,
194, 167, 92, 42, 221, 153, 30, 224, 116, 34, 94, 144, 89, 163, 78, 102, 198, 66,
40, 200, 109, 65, 133, 96, 10, 79, 5, 184, 203, 242, 222, 187, 63, 207, 45, 249,
25, 138, 76, 68, 62, 136, 239, 179, 54, 58, 121, 27, 117, 150, 213, 158, 110, 61,
251, 123, 44, 37, 211, 84, 67, 174, 120, 122, 218, 31, 134, 9, 196, 128, 98, 91,
164, 101, 80, 217, 154, 86, 100, 172, 93, 15, 254, 59, 147, 118, 105, 253, 216)


class PerlinBase(object):
  def __init__(self, amplitude : float, ampl_scale : float, frequency : float, freq_scale: float,
               octaves : int, scale_range : None):
    self.rand_ord_0_to_255 = [ i for i in range(256) ]
    random.shuffle(self.rand_ord_0_to_255)
    self.rand_ord_0_to_255 = tuple(self.rand_ord_0_to_255)

    # Configurables
    self.ampl = amplitude
    self.ampl_scale = ampl_scale
    self.freq = frequency
    self.freq_scale = freq_scale
    self.octaves = octaves
    if scale_range and not isinstance(scale_range, (list, tuple)):
      raise TypeError("Scale range must be None or tuple with two integer values")
    self.scale_r = scale_range # (bottom, top)

    # Constants
    self.PERMUTATED_LIST = PERMUTATION_SOURCE
    self.LAT_POINTS = None # Lattice points from floored position

  def vlen(self, v):
    return math.sqrt( sum([i * i for i in v]) )

  def dot(self, v1, v2):
    return sum([i * j for (i, j) in zip(v1, v2)])

  def normalize(self, v):
    l = self.vlen(v)
    return [ e / l for e in v ]

  def scale_value(self, value):
    low, high = self.scale_r
    value = (value + 1.0) / 2.0 # [-1, 1] -> [0, 1]
    return int((high - low) * value + low)

  def calc_fade(self, point : float):
    return point * point * point * (point*(point*6.0 - 15.0) + 10.0)

  def calc_gradient(self, point : float):
    pass

  def calc_octaves(self, point : float):
    pass


class Perlin1D(PerlinBase):
  def __init__(self, amplitude : float, ampl_scale : float, frequency : float, freq_scale: float,
               octaves : int, scale_range : None):
    super().__init__(amplitude, ampl_scale, frequency, freq_scale, octaves, scale_range)
    self.LAT_POINTS = (-1.0, 1.0)


  def calc_gradient(self, point):
    rand = self.rand_ord_0_to_255[int(point) & 0xff]
    point = self.PERMUTATED_LIST[rand & 0xff]
    return self.LAT_POINTS[0] if (self.PERMUTATED_LIST[point] / 256.0) < 0.5 else self.LAT_POINTS[1]


  def calc_noise(self, point : float):
    p0 = math.floor(point)
    p1 = p0 + 1.0

    faded = self.calc_fade(point - p0)

    g0 = self.calc_gradient(p0)
    g1 = self.calc_gradient(p1)

    return (1.0 - faded) * g0 * (point - p0) + faded * g1 * (point - p1)


  def calc_octaves(self, point):
    res = 0.0
    for i in range(self.octaves):
      freq = (self.freq / 2**i) * self.freq_scale
      ampl = (self.ampl / 2**i) * self.ampl_scale
      res += self.calc_noise(point * (1.0 / freq)) * ampl

    if self.scale_r:
      res = self.scale_value(res)

    return res


class Perlin2D(PerlinBase):
  def __init__(self, amplitude : float, ampl_scale : float, frequency : float, freq_scale: float,
               octaves : int, scale_range : None):
    super().__init__(amplitude, ampl_scale, frequency, freq_scale, octaves, scale_range)
    self.LAT_POINTS = (
      (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)
    )
    self.VECTORS = (
      (1.0, 0.0),
      (1.0, 1.0),
      (0.0, 1.0),
      (-1.0, 1.0),
      (-1.0, 0.0),
      (-1.0, -1.0),
      (0.0, -1.0),
      (1.0, -1.0),
    )


  def calc_gradient(self, lat_point : tuple):
    # Get random gradient vector
    P = self.rand_ord_0_to_255
    i, j = int(lat_point[0]), int(lat_point[1])
    x = P[P[P[i & 0xff]]]
    y = (P[x] + P[j & 0xff]) & 0xff
    x /= 0xff
    y /= 0xff
    x = (x * 2.0) - 1.0
    y = (y * 2.0) - 1.0

    return self.normalize((x, y))


  def calc_noise(self, point : tuple):
    subtr = lambda p1, p2 : (p1[1] - p2[1], p1[0] - p2[0]) # Subtract for 2D vectors

    p0 = (math.floor(point[0]), math.floor(point[1]))
    p1 = (p0[0] + self.LAT_POINTS[0][0], p0[1] + self.LAT_POINTS[0][1])
    p2 = (p0[0] + self.LAT_POINTS[1][0], p0[1] + self.LAT_POINTS[1][1])
    p3 = (p0[0] + self.LAT_POINTS[2][0], p0[1] + self.LAT_POINTS[2][1])

    g0 = self.calc_gradient(p0)
    g1 = self.calc_gradient(p1)
    g2 = self.calc_gradient(p2)
    g3 = self.calc_gradient(p3)

    h_faded = self.calc_fade(point[0] - p0[0]) # Horizontal
    v_faded = self.calc_fade(point[1] - p0[1]) # Vertical

    p0_p1 = (1.0 - h_faded) * self.dot(g0, subtr(point, p0)) + h_faded * self.dot(g1, subtr(point, p1))
    p2_p3 = (1.0 - h_faded) * self.dot(g2, subtr(point, p2)) + h_faded * self.dot(g3, subtr(point, p3))

    res = (1.0 - v_faded) * p0_p1 + v_faded * p2_p3

    return res


  def calc_octaves(self, point : tuple):
    res = 0.0
    for i in range(self.octaves):
      freq = (self.freq / 2**i) * self.freq_scale
      ampl = (self.ampl / 2**i) * self.ampl_scale
      p = (point[0] * (1.0 / freq), point[1] * (1.0 / freq))
      res += self.calc_noise(p) * ampl

    if self.scale_r:
      res = self.scale_value(res)

    return res


class Perlin3D(PerlinBase):
  def __init__(self, amplitude : float, ampl_scale : float, frequency : float, freq_scale: float,
               octaves : int, scale_range : None):
    super().__init__(amplitude, ampl_scale, frequency, freq_scale, octaves, scale_range)
