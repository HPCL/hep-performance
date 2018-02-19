#!/bin/bash

#./mkFit/mkFit --num-tracks 5000 --num-events 10000 --write --file-name simtracks_barrel_large.bin

NT=10

EXP=real_scaling

tau experiment select $EXP

#CMDp1=tau_exec\ -T\ papi,icpc,pdt,tbb,serial\ -ebs\ -ebs_period=10039
#CMDp2=./mkFit/mkFit\ --read\ --file-name\ simtracks_barrel_5k_tracks_1k_events.bin\ --num-thr\ $NT\ --fit-std-only\ --silent
CMDp2=./mkFit/mkFit\ --cmssw-n2seeds\ --input-file\ TTbar35PU-memoryFile.fv3.clean.writeAll.recT.072617.bin\ --build-ce\ --num-thr\ $NT\ --num-events\ 100

measure_list=(scalar_simd packed_simd tot_cyc tot_ins tcm2 res_stl tca2 lst tcm1 llc_ref llc_miss)

function run_trials {

	for i in ${measure_list[@]}; do
		tau experiment edit $EXP --measurement $i
		tau trial create $CMD
	done

}

for i in {10..100..10}
do
NT=$i
CMDp2=./mkFit/mkFit\ --cmssw-n2seeds\ --input-file\ TTbar35PU-memoryFile.fv3.clean.writeAll.recT.072617.bin\ --build-ce\ --num-thr\ $NT\ --num-events\ 100 
run_trials
done



