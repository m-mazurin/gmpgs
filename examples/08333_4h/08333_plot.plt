set encoding koi8r
set terminal postscript enhanced eps color font "Times New Roman, 12"
set output "08333.eps"

set xrange [10:80]
set xlabel "2{/Symbol Q}, {/Symbol \260}" font ",22"
set ylabel "Интенсивность, у.е." font ",22"
set xtics font ",18"
set ytics font ",18"
set key font ",22"

plot\
"08333_points.dat" using 1:2 title "Y_{эксп.}" with points pt 6 ps 0.25 lc rgb 'black',\
"08333_points.dat" using 1:3 title "Y_{расч.}" with lines ls 1 lw 2 lc rgb 'red',\
"08333_points.dat" using 1:4 title "Y_{эксп.}-Y_{расч.}" with lines ls 1 lc 18,\
"08333_peaks.dat" using 1:2 with points pt "|" ps 0.1 lc rgb 'blue' title "Брэгговские позиции"