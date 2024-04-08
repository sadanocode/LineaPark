## Запуск протестирован на Ubuntu 20.04

Распакуем
```
unzip /root/LineaPark-free.zip
```
или же скачаем с гитхаба
```
git clone https://github.com/Genndoso/LineaPark
```
Проверим список версий  и выбор 3.11:
```
python3 --version
update-alternatives --list python3
update-alternatives --config python3
```
создадим сессию
```
tmux new -s lineapark
```
что бы потом заходить
```
tmux attach -t lineapark
```
И посде создания сессии начнем настройку и установку зависимостей
```
cd /root/LineaPark-free
python3.11 -m venv /root/LineaPark-free/venv
source /root/LineaPark-free/venv/bin/activate
cd /root/LineaPark-free
pip install -r requirements.txt
pip install requests
python main.py
```
