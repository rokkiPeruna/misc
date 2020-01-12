#!/usr/bin/bash

default_rounds=1000000
rounds="$default_rounds"
separator="--------------------------"
python_itrp=$(which python3)
ccompiler=$(which g++)
cprog="bertnard_box"
cname="bertnard_box.cpp"
pyname="bertnard_box.py"

if [ ! ${python_itrp} ]
then
  echo "No Python3 available!"
  exit 1
fi

if [ ! ${ccompiler} ]
then
  echo "No g++ compiler available!"
  exit 2
fi

if [ ! -f "$(pwd)/${cname}" ] || [ ! -f "$(pwd)/${pyname}" ]
then
  echo "Run script in source folder!"
  exit 3
fi

if [ ! -f "$(pwd)/${cprog}" ]
then
  ${ccompiler} -Wall -std=c++11 -o bertnard_box bertnard_box.cpp
  if [ ! $? ]
  then
    echo "Compilation failed!"
    exit 4
  fi
fi

if [ $1 ]
then
  rounds=$1
fi

echo ${separator}
echo "Running C++ implementation..." 
echo ${separator}
./${cprog} ${rounds}
echo ${separator} 

echo "Running Python3 implementation..."
echo ${separator} 
${python_itrp} ${pyname} ${rounds}
echo ${separator} 

echo "Ran both!"
