set encoding koi8r
set terminal postscript enhanced eps color font "Times New Roman, 12"
set output "08150.eps"

set xrange [10:80]
set xlabel "2{/Symbol Q}, {/Symbol \260}" font ",22"
set ylabel "�������������, �.�." font ",22"
set xtics font ",18"
set ytics font ",18"
set key font ",22"

plot\
"08150_points.dat" using 1:2 title "Y_{����.}" with points pt 6 ps 0.25 lc rgb 'black',\
"08150_points.dat" using 1:3 title "Y_{����.}" with lines ls 1 lw 2 lc rgb 'red',\
"08150_points.dat" using 1:4 title "Y_{����.}-Y_{����.}" with lines ls 1 lc 18,\
"08150_peaks.dat" using 1:2 with points pt "|" ps 0.1 lc rgb 'blue' title "����������� �������"