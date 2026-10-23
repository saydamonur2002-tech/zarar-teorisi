f=$1; n=$(pdfinfo $f.pdf | awk '/Pages/{print $2}'); : > loc_$f.txt
for i in $(seq 1 $n); do pdftoppm -f $i -l $i -r 90 -gray -png $f.pdf q_${f}_$i; t=$(tesseract q_${f}_$i*.png - -l tur 2>/dev/null | tr '\n' ' '); rm -f q_${f}_$i*.png
 echo "$t" | grep -qiE "faiz (dışı|hariç)|vergi yükü|program tanımlı" && echo "$i $(echo "$t" | grep -oiE 'tablo[^.]{0,60}' | head -2 | tr '\n' '|')" >> loc_$f.txt; done
echo DONE >> loc_$f.txt
