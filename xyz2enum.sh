#!/bin/bash 

# xyzfile=$1;

usage(){
    echo "DESCRIPTION:";
    echo -e "\t Transform 'xyz' style files into 'enum.in' format files, which can be used directly by enum.x."
    echo -e "\t Eg. enum.x enum.in. You may also interest in 'enum2xyz.sh'."
    echo "USAGE:";
    echo -e "\t cat xyz | xyz2enum.sh -m 'comments' -n nat -s 'list';"
    echo -e "\t    -m: comments about the system, which will be printed at the first line in 'enum.in';"
    echo -e "\t    -n: nat types of different atoms;"
    echo -e "\t    -s: specify possbile atomic specieses in each sublattice; the format should be like 0/1/2/...,"
    echo -e "\t        where those numbers indicate different types of elements. For more details about "
    echo "EXAMPLES:"
    echo -e 'cat xyz | xyz2enum.sh -m "Al2CoNi" -n 3 -s "0 1/2" ';
    exit;
}

surf=0;
at=1;
precision=0.0001;
size="1 1";
while getopts "m:n:s:S:c:fp:" opt;
do
    case $opt in
	m)			# comments, usually appear on the first line
	   comment=$OPTARG
	   ;;
	n)			# number of atomic types
	   nat=$OPTARG;
	   ;;
	s)			# possible atom types in each sublattice
	   sublist=($OPTARG);
	   ;;
	S)			# starting and ending cell sizes for search
	   size=$OPTARG;
	   ;;
	f)			# use surface instead of bulk
	   surf=1
	   ;;
	p)
	   precision=$OPTARG 	# finite precision
	   ;;
	h|*)
	   usage
	   ;;
    esac
done

echo "$comment";
if [ $surf -eq 1 ];
then
    echo "surf";
else
    echo "bulk";
fi

count=0;
while read line;
do
    case $count in
	0)
	   ax=`echo $line | awk '{print $1}'`;
	   ay=`echo $line | awk '{print $2}'`;
	   az=`echo $line | awk '{print $3}'`;
	   count=$(( $count + 1 ));
	   echo $line;
	   ;;
	1)
	   bx=`echo $line | awk '{print $1}'`;
	   by=`echo $line | awk '{print $2}'`;
	   bz=`echo $line | awk '{print $3}'`;
	   count=$(( $count + 1 ));
	   echo $line;
	   ;;
	2)
	   cx=`echo $line | awk '{print $1}'`;
	   cy=`echo $line | awk '{print $2}'`;
	   cz=`echo $line | awk '{print $3}'`;
	   count=$(( $count + 1 ));
	   echo $line;
	   ;;
	3)
	   an=`echo $line | awk '{print $1}'`;
	   count=$(( $count + 1 ));
	   echo -e "$nat\t# -nary case";
	   echo -e "$an\t# atoms in a unit cell";
	   ;;
	*)
	   count=$(( $count + 1 ));
	   
	   # n1 n2 n3: relative position
	   # at: atomic type; st: sublattice type; as: atomic symbol;
	   read n1 n2 n3 at st as <<<`echo $line`;
	   
	   #  n1 n2 n3 --> x y z in real space;
	   x=`echo "scale=8; ($n1*$ax + $n2*$bx + $n3*$cx)/1 " | bc | awk '{printf "%14.8f",$1}'`;
	   y=`echo "scale=8; ($n1*$ay + $n2*$by + $n3*$cy)/1 " | bc | awk '{printf "%14.8f",$1}'`;
	   z=`echo "scale=8; ($n1*$az + $n2*$bz + $n3*$cz)/1 " | bc | awk '{printf "%14.8f",$1}'`;
	   #echo $x-$y-$z-$at-$st-$as;
	   echo -e "$x $y $z ${sublist[$(( $st-1 ))]}  \t# s$st";
	   ;;
    esac
done

echo "";
tail -n +5 $xyzfile | awk '{print $1,$2,$3,"\t0/1"}';
echo -e "$size \t# Starting and ending cell sizes for search"
echo -e "$precision\t# Epsilon (finite precision paramter)"
echo -e "full\t# list of labelings"
#echo "0 2 2" 
#echo "0 2 2"
