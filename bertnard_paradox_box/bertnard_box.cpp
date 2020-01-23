#include <iostream>
#include <string>
#include <random>
#include <functional>
#include <chrono>

using namespace std;

const int GOLD = 1;
const int SILVER = 0;

const vector<vector<int>> boxes = {
  {GOLD, GOLD},
  {GOLD, SILVER},
  {SILVER, SILVER}
};

const int NUM_BOXES = boxes.size();
const int NUM_COINS = boxes.at(0).size();
const int DEF_ROUNDS = 1000000;

int main(int argc, char* argv[]) {
  int rounds = DEF_ROUNDS;
  if (argc > 1) {
    rounds = stoi(argv[1]);
  }
  cout << "Calculating " << rounds << " rounds.." << endl;

  default_random_engine pick_generator;
  uniform_int_distribution<int> coin_distribution(0, NUM_COINS - 1);
  uniform_int_distribution<int> box_distribution(0, NUM_BOXES - 1);
  auto pick_coin = bind(coin_distribution, pick_generator);
  auto pick_box = bind(box_distribution, pick_generator);
  
  int hits = 0;
  int misses = 0;

  int i = 0;
  auto start_time = chrono::high_resolution_clock::now();
  while (i < rounds) {
    auto picked_box = boxes.at(pick_box());
    auto picked_coin_idx = picked_box.at(pick_coin());

    if (picked_coin_idx) {
      i += 1;
      if (picked_box.at(1 - picked_box.at(picked_coin_idx)))
        hits += 1;
      else
        misses += 1;
    }
  }
  auto end_time = chrono::high_resolution_clock::now();
  auto loop_time = chrono::duration_cast<chrono::microseconds>(end_time - start_time).count();

  cout << "Hits: " << hits << endl;
  cout << "Misses: " << misses << endl;
  cout << "Hit percent: " << float(hits) / rounds * 100.0f << endl;
  cout << "Miss percent: " << float(misses) / rounds * 100.0f << endl;
  cout << "Calculation time: " << loop_time / 1000000.0f << " seconds" << endl;
}
