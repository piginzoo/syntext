if [ "$2" = "" ]; then
    echo "Usage: run.sh --dir output_dir --worker worker_number --num number <--debug>"
    exit
fi

python -m syntext.main $*