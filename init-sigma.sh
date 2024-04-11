#!/bin/bash

# Stop streamlit process when quitting with Ctrl-c.
trap 'ctrl_c' EXIT
function ctrl_c() {
  if pgrep -x streamlit > /dev/null; then
    echo "Stopping streamlit..."
    kill `pgrep -f streamlit`
  fi
}

# Ensure tmux is installed (for running streamlit server in the background).
if ! command -v tmux &> /dev/null; then
  sudo yum install -y tmux
fi

# Ensure we show a message on login about attaching to tmux.
if ! grep -q sigma ~/.bash_profile; then
  echo "" >> ~/.bash_profile
  echo "echo ''" >> ~/.bash_profile
  echo "echo '#############################'" >> ~/.bash_profile
  echo "echo '#                           #'" >> ~/.bash_profile
  echo "echo '#  Reattach to sigma with:  #'" >> ~/.bash_profile
  echo "echo '#                           #'" >> ~/.bash_profile
  echo "echo '#     tmux a -t sigma       #'" >> ~/.bash_profile
  echo "echo '#                           #'" >> ~/.bash_profile
  echo "echo '#############################'" >> ~/.bash_profile
  echo "echo ''" >> ~/.bash_profile
fi

# Ensure we're not running multiple copies of this script.
if pgrep -x "streamlit" > /dev/null; then
  echo "streamlit is already running. Attach to the tmux session with:"
  echo "   tmux a -t sigma"
  echo "Exiting."
  exit 1
fi

# Ensure we're in a tmux session (so we can detach and run in background).
if [ -z "$TMUX" ]; then
  echo "Start a tmux session first before running this script:"
  echo "   tmux new -s sigma"
  echo "Exiting."
  exit 1
fi

# Ensure git is installed (for cloning EngageBot from github).
if ! command -v git &> /dev/null; then
  sudo yum install -y git
fi

# Ensure nginx is installed and configured.
if [ ! -f /etc/nginx/conf.d/websocket-streamlit.conf ]; then
  # Install nginx from amazon-linux-extras.
  sudo amazon-linux-extras install -y nginx1
  # Configure reverse proxy for streamlit port 8051.
  cat <<EOF | sudo tee /etc/nginx/conf.d/websocket-streamlit.conf
upstream streamlit            { server localhost:8501; }

upstream streamlit-nsc396a-1  { server localhost:8601; }
upstream streamlit-nsc396a-2  { server localhost:8602; }
upstream streamlit-nsc396a-3  { server localhost:8603; }
upstream streamlit-nsc396a-4  { server localhost:8604; }
upstream streamlit-nsc396a-5  { server localhost:8605; }
upstream streamlit-nsc396a-6  { server localhost:8606; }
upstream streamlit-nsc396a-7  { server localhost:8607; }
upstream streamlit-nsc396a-8  { server localhost:8608; }
upstream streamlit-nsc396a-9  { server localhost:8609; }
upstream streamlit-nsc396a-10 { server localhost:8610; }

upstream streamlit-gist330-1  { server localhost:8701; }
upstream streamlit-gist330-2  { server localhost:8702; }
upstream streamlit-gist330-3  { server localhost:8703; }
upstream streamlit-gist330-4  { server localhost:8704; }
upstream streamlit-gist330-5  { server localhost:8705; }
upstream streamlit-gist330-6  { server localhost:8706; }
upstream streamlit-gist330-7  { server localhost:8707; }
upstream streamlit-gist330-8  { server localhost:8708; }
upstream streamlit-gist330-9  { server localhost:8709; }
upstream streamlit-gist330-10 { server localhost:8710; }

server {
  listen 80;
  server_name localhost;

  # Proxy requests to a backend mapped to a specific port per streamlit process.
  location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_redirect off;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Default streamlit port.
    proxy_pass http://streamlit;

    # Custom ports for different streamlit processes serving each course/week.
    location ^~ /nsc396a/1/  { proxy_pass http://streamlit-nsc396a-1/; }
    location ^~ /nsc396a/2/  { proxy_pass http://streamlit-nsc396a-2/; }
    location ^~ /nsc396a/3/  { proxy_pass http://streamlit-nsc396a-3/; }
    location ^~ /nsc396a/4/  { proxy_pass http://streamlit-nsc396a-4/; }
    location ^~ /nsc396a/5/  { proxy_pass http://streamlit-nsc396a-5/; }
    location ^~ /nsc396a/6/  { proxy_pass http://streamlit-nsc396a-6/; }
    location ^~ /nsc396a/7/  { proxy_pass http://streamlit-nsc396a-7/; }
    location ^~ /nsc396a/8/  { proxy_pass http://streamlit-nsc396a-8/; }
    location ^~ /nsc396a/9/  { proxy_pass http://streamlit-nsc396a-9/; }
    location ^~ /nsc396a/10/ { proxy_pass http://streamlit-nsc396a-10/; }
    location ^~ /gist330/1/  { proxy_pass http://streamlit-gist330-1/; }
    location ^~ /gist330/2/  { proxy_pass http://streamlit-gist330-2/; }
    location ^~ /gist330/3/  { proxy_pass http://streamlit-gist330-3/; }
    location ^~ /gist330/4/  { proxy_pass http://streamlit-gist330-4/; }
    location ^~ /gist330/5/  { proxy_pass http://streamlit-gist330-5/; }
    location ^~ /gist330/6/  { proxy_pass http://streamlit-gist330-6/; }
    location ^~ /gist330/7/  { proxy_pass http://streamlit-gist330-7/; }
    location ^~ /gist330/8/  { proxy_pass http://streamlit-gist330-8/; }
    location ^~ /gist330/9/  { proxy_pass http://streamlit-gist330-9/; }
    location ^~ /gist330/10/ { proxy_pass http://streamlit-gist330-10/; }
  }
}
EOF
  # Run nginx on boot.
  sudo systemctl enable nginx.service
fi
# Ensure nginx is started.
sudo systemctl start nginx.service

# Ensure modern python is installed via pyenv and pyenv-virtualenv.
# Problem: app dependencies require urllib3, which requires openssl > 1.0, which
# Amazon Linux 2 python packages are not compiled against.
# Solution: Build python from source against openssl 1.1.1+ using pyenv below.
# See: https://github.com/urllib3/urllib3/issues/2168
# See: https://urllib3.readthedocs.io/en/latest/v2-migration-guide.html#common-upgrading-issues
if [ ! -d ~/.pyenv ]; then
  # Install pyenv for installing a modern python version not in Amazon Linux 2.
  git clone https://github.com/pyenv/pyenv ~/.pyenv
  # Add pyenv to shell init.
  echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
  echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
  echo -e '\n# Pyenv.\nif command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
  exec "$SHELL"
  # Install newer version of openssl that urllib3 v2+ requires.
  sudo yum install -y openssl11 openssl11-devel
  # Install dependencies for building python from source.
  sudo yum install -y gcc
  sudo yum install -y zlib-devel
  sudo yum install -y xz xz-devel
  sudo yum install -y bzip2 bzip2-devel
  sudo yum install -y readline-devel
  sudo yum install -y sqlite sqlite-devel
  sudo yum install -y tk-devel libffi-devel
  # Install and use modern python via pyenv.
  pyenv install 3.12.0
  pyenv local 3.12.0
fi

# Ensure app is installed.
if [ ! -d ~/EngageBot ]; then
  # Clone app repo (EngageBot).
  git clone https://github.com/DrJKevan/EngageBot ~/EngageBot

  # Set up a virtualenv for python dependencies via pyenv-virtualenv plugin.
  # See: https://github.com/pyenv/pyenv-virtualenv#installation
  git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
  exec "$SHELL"
  cd ~/EngageBot/ && pyenv virtualenv 3.12.0 venv_engagebot
  echo "venv_engagebot" > ~/EngageBot/.python_version
  pyenv activate venv_engagebot

  # Update (venv) python pip to latest.
  python -m pip install --upgrade pip

  # Install python dependencies for app.
  pip install -r requirements.txt
fi

# Ensure environment variables are set.
#if [ ! -v OPENAI_API_KEY ] && ! $(grep -q OPENAI_API_KEY ~/EngageBot/.env); then
#  echo -e "OPENAI_API_KEY not found in ~/EngageBot/.env. Add it now: "
#  read -r -s OPENAI_API_KEY
#  export OPENAI_API_KEY="${OPENAI_API_KEY}"
#fi
if [ ! -v PG_HOST ] && ! $(grep -q PG_HOST ~/EngageBot/.env); then
  echo -e "PG_HOST not found in ~/EngageBot/.env. Add it now: "
  read -r -s PG_HOST
  export PG_HOST="${PG_HOST}"
fi
if [ ! -v PG_PORT ] && ! $(grep -q PG_PORT ~/EngageBot/.env); then
  echo -e "PG_PORT not found in ~/EngageBot/.env. Add it now: "
  read -r -s PG_PORT
  export PG_PORT="${PG_PORT}"
fi
if [ ! -v PG_USER ] && ! $(grep -q PG_USER ~/EngageBot/.env); then
  echo -e "PG_USER not found in ~/EngageBot/.env. Add it now: "
  read -r -s PG_USER
  export PG_USER="${PG_USER}"
fi
if [ ! -v PG_PASS ] && ! $(grep -q PG_PASS ~/EngageBot/.env); then
  echo -e "PG_PASS not found in ~/EngageBot/.env. Add it now: "
  read -r -s PG_PASS
  export PG_PASS="${PG_PASS}"
fi
if [ ! -v PG_DB ] && ! $(grep -q PG_DB ~/EngageBot/.env); then
  echo -e "PG_DB not found in ~/EngageBot/.env. Add it now: "
  read -r -s PG_DB
  export PG_DB="${PG_DB}"
fi

# Show message how to detach from tmux session.
echo "####################################################"
echo "#################### IMPORTANT #####################"
echo "#                                                  #"
echo "#   To detach from this tmux session and leave     #"
echo "#   it running in the background, enter:           #"
echo "#      ctrl-b d                                    #"
echo "#   (Hold ctrl key and the b key and release,      #"
echo "#   then type the d key)                           #"
echo "#                                                  #"
echo "#   Then you can exit your ssh session.            #"
echo "#                                                  #"
echo "#   You may reattach later with 'tmux a -t sigma'  #"
echo "#                                                  #"
echo "#   Quit streamlit with ctrl-c when attached.      #"
echo "#                                                  #"
echo "####################################################"

# Run app(s).
cd ~/EngageBot

#streamlit run nsc396a/nsc396a_interaction1.py --server.port 8601 &
streamlit run nsc396a/nsc396a_interaction2.py --server.port 8602 &
streamlit run nsc396a/nsc396a_interaction3.py --server.port 8603 &
streamlit run nsc396a/nsc396a_interaction4.py --server.port 8604 &
#streamlit run nsc396a/nsc396a_interaction5.py --server.port 8605 &
#streamlit run nsc396a/nsc396a_interaction6.py --server.port 8606 &
#streamlit run nsc396a/nsc396a_interaction7.py --server.port 8607 &
#streamlit run nsc396a/nsc396a_interaction8.py --server.port 8608 &
#streamlit run nsc396a/nsc396a_interaction9.py --server.port 8609 &
#streamlit run nsc396a/nsc396a_interaction10.py --server.port 8610 &
#streamlit run gist330/gist330_interaction1.py --server.port 8701 &
streamlit run gist330/gist330_interaction2.py --server.port 8702 &
streamlit run gist330/gist330_interaction3.py --server.port 8703 &
streamlit run gist330/gist330_interaction4.py --server.port 8704 &
#streamlit run gist330/gist330_interaction5.py --server.port 8705 &
#streamlit run gist330/gist330_interaction6.py --server.port 8706 &
#streamlit run gist330/gist330_interaction7.py --server.port 8707 &
#streamlit run gist330/gist330_interaction8.py --server.port 8708 &
#streamlit run gist330/gist330_interaction9.py --server.port 8709 &
#streamlit run gist330/gist330_interaction10.py --server.port 8710 &
