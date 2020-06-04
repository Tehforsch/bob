if [[ $# == 0 ]]; then
    exit 0
fi
rm bob/localConfig.py
ln -s $(realpath localConfigs/$1.py) $(realpath bob/localConfig.py)
