if [ "$2" = "" ]; then
    echo "Usage: run.sh --dir output_dir --num number <--debug>"
    echo "Example: run.sh data/output/ 1000"
    exit
fi

python -m syntext.main $*