if [ "$2" = "" ]; then
    echo "Usage: run.sh output_dir number"
    echo "Example: run.sh data/output/ 1000"
    exit
fi

python -m syntext.main --dir $1 --num $2