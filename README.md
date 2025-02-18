This repo contains three examples
---------------------------------

1. helloworld
This is a simple example to show how to communicate with ChatGPT API using Python

2. coffeeshop
This shows how to use ChatGPT API (OpenAI APIs) to create simple chatbots with history

3. shoerack
This shows how you can build a RAG based ChatGPT with history, using 
LangChain, Chroma vector store and OpenAI embeddings.

Steps to run the examples
-------------------------
1. 
    Go to the directory where the python program is located.
    For example, to run hello-world.py, first cd to the helloworld directory
        cd helloworld

2.
    Setup a virtual environment.
    For example, on the mac, type
        python -m venv [name_of_env]

    Note: These examples were set up to run on Python Version 3.12 and Pip3
    To find out the version of python and pip on your system, type
        python --version
        pip --version

    On Windows,
        Follow commands provided in the presentation

3.  Activate the virtual environment
    For example, on the mac, type
        source [name_of_env]/bin/activate

    On Windows,
        Follow commands provided in the presentation

4.
    Install all the required libraries.
    Type
        pip install -r requirements.txt

5.
    Run the python program in the directory.
    For example, inside helloworld directory,
    Type
        python hello-world.py

6.
    After you are done, deactivate the environment.
    Type
        deactivate