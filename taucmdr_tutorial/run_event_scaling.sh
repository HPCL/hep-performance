#!/bin/bash


# parameters for mkFit
NT=10 # number of threads
NE=10 # number of simulated events
FILE=TTbar70PU-memoryFile.fv3.clean.writeAll.recT.072617.bin # input file name

# parameters for TAU
EXP=event_scaling_TTbar70  # experiment name - must be created before running this script
tau experiment select $EXP # switch tau to this experiment

# command to execute the mkFit program
#    note the '\' before each space
#    also this must be redefined inside the loop to overwrite the variable as they vary
CMD=./mkFit/mkFit\ --cmssw-n2seeds\ --input-file\ $FILE\ --build-ce\ --num-thr\ $NT\ --num-events\ $NE


measure_list=(scalar_simd packed_simd tot_cyc tot_ins tcm2 res_stl tca2 lst tcm1 llc_ref llc_miss)

function run_trials {

	for i in ${measure_list[@]}; do
		tau experiment edit $EXP --measurement $i
		tau trial create $CMD
	done

}

for i in {10..100..10}
do
NE=$i
CMD=./mkFit/mkFit\ --cmssw-n2seeds\ --input-file\ $FILE\ --build-ce\ --num-thr\ $NT\ --num-events\ $NE 
run_trials
done



