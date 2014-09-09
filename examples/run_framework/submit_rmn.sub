#!/bin/bash
#$ -V
#$ -pe 12way 24 
#$ -q development
#$ -cwd
#$ -N test_pad
#$ -j n
#$ -o $JOB_NAME.o.$JOB_ID
#$ -e $JOB_NAME.e.$JOB_ID
#$ -M youremail@place.edu
#$ -m be
#$ -l h_rt=00:05:00

python run_lonestar_test.py
