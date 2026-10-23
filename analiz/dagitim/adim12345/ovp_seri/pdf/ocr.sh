f=$1; n=$(pdfinfo $f.pdf | awk '/Pages/{print $2}'); s=$((n-14)); [ $s -lt 1 ] && s=1
pdftoppm -f $s -l $n -r 170 -gray -png $f.pdf o_$f
for p in o_$f*.png; do tesseract $p - -l tur --psm 6 2>/dev/null; echo "=====PAGE $p"; done > $f.txt
