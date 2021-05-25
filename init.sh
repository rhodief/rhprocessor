#!/bin/bash
echo "Iniciando Script: Senha #-> gpu-jupyter <-#"
echo "Ver https://hub.docker.com/r/cschranz/gpu-jupyter"
docker run --gpus all -it -p 8848:8888 -v $(pwd):/home/jovyan/work -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes --shm-size 8G  --user root cschranz/gpu-jupyter:v1.3_cuda-10.2_ubuntu-18.04_python-only
echo "Terminado"