working_dir=$1
script_dir=$2
for f in ${working_dir}/???????.txt; do vim -c "source ${script_dir}/coordinate_XY_to_jsn.vim | wq! ${f%.txt}.jsn" $f; done
