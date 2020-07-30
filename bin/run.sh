if [ "$1" = "stop" ]; then
    echo "Terminate the generator ..."
    ps aux|grep python|grep syntext.main|awk '{print $2}'|xargs kill -9
    exit
fi

if [ "$2" = "" ]; then
    echo "Usage: bin/run.sh --dir output_dir --worker worker_number --num number --config config.yml <--debug>"
    echo "    captcha gen: bin/run.sh --dir data/output --worker 3 --num 100 --config config/config.captcha.yml --debug"
    echo "    english gen: bin/run.sh --dir data/output --worker 3 --num 100 --config config/config.alphabeta.yml --debug"
    echo "    coutour gen: bin/run.sh --dir data/output --worker 3 --num 100 --config config/config.contour.yml --debug"
    echo "    corpus  gen: bin/run.sh --dir data/output --worker 3 --num 100 --config config/config.corpus.yml --debug"
    exit
fi

last_arg=${@:$#}
if [ "$last_arg" = "--debug" ]; then
    python -m syntext.main $*
else
    nohup python -m syntext.main $*>data/log.txt 2>&1 &
fi

