#!/bin/bash

# 46 gb
# 47 gbc
system=47
folder=gbc
#for i in {1..1443}
for i in 234
do
	read num < <(printf "%04d" $i)
	#num=$(printf "%04d" $i)
	#if [ $((i % 10)) -eq 0 ]
	#then
		echo ${num}
		sleep 2
	#fi
	curl -o ${folder}/${num}.html https://datomatic.no-intro.org/index.php?page=show_record\&s=${system}\&n=${num} &> ${folder}/${num}.log &
done