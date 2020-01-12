#include <iostream>
#include <random>
#include <functional>

using namespace std;

const vector<vector<int, int>> boxes = {
  {1, 1},
  {1, 0},
  {0, 0}
};

const int NUM_BOXES = boxes.size();
const int NUM_COINS = boxes.at(0).size();
const int DEF_ROUNDS = 1000000;

void main(int argc, char* argv) {
  int rounds = DEF_ROUNDS;
  if (argc) {
    rounds = static_cast<int>(argv[1]);
  }

  default_random_engine pick_generator;
  uniform_int_distribution<char> coin_distribution(0, NUM_COINS - 1);
  uniform_int_distribution<char> box_distribution(0, NUM_BOXES - 1);
  auto pick_coin = bind(coin_distribution, pick_generator);
  auto pick_box = bind(box_distribution, pick_generator);
  
  int hits = 0;
  int misses = 0;

  int i = 0;
  while (i < rounds) {
    auto picked_box = boxes.at(pick_box());
    auto picked_coin = picked_box.at(pick_coin());
    if (picked_coin) {
      i += 1;
      if (picked_box.at(1 - picked_coin))
        hits += 1;
      else
        misses += 1;
    }
  }

  cout << "Hits: " << hits << endl;
  cout << "Misses: " << misses << endl;
  cout << "Hit percent: " << hits / rounds * 100.0f << endl;
  cout << "Miss percent: " << misses / rounds * 100.0f << endl;
}
