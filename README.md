This contains code for a RAG based chatbot built using ChatGPT.

Name the flask app application.py.  This is IMPORTANT!

To start the flask app
    python application.py
To install in ec2 linux
    #!/bin/bash
    sudo yum -y install python-pip
    python3 -m pip install --upgrade pip
    cd /home/ec2-user
    aws s3 cp --recursive s3://maistro.thirukkural.chatbot.code .
    python3 -m venv virtenv
    source virtenv/bin/activate
    python3 -m pip install -r requirements.txt
    export OPENAI_API_KEY="xxx"
    nohup gunicorn -b 0.0.0.0:8000 application:app &

To test locally
    python terminal-chat.py

Create the virtual env and test the app
    python -m venv macenv
    source macenv/bin/activate
    python -m pip install -r requirements.txt
    python application.py
    on another terminal window
        source macenv/bin/activate
        python chat.py

Initialize elastic beanstalk
    eb init -p python-3.12 eb-chatbot --region us-east-1 --profile maistro-admin

(Optional) Configure default keypair
    eb init --profile maistro-admin

Create environment and deploy app with eb create
    eb create eb-chatbot-env --vpc.publicip --profile maistro-admin

Open and test website
    eb open --profile maistro-admin
    (You should get hello message from chatbot when you hit the URL)
    
Terminate environment
    eb terminate --profile maistro-admin