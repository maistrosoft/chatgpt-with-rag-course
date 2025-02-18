import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

#all langchain imports
from langchain_openai import ChatOpenAI

from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders import TextLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import json
import config

from langchain_core.messages import HumanMessage

from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain.chains import create_retrieval_chain

#what does this app do?
#1. load the product catalog
#2. split the product catalog into chunks
#3. create a vector store from the chunks
#4. create a retriever from the vector store
#5. create a document chain from the retriever
#6. create a conversation chain from the document chain
#7. start the conversation loop

#global variables for this app
model = config.MODEL
temperature = config.TEMPERATURE
llm = ChatOpenAI(model=model, temperature=temperature)
chatHistory = {} #each id has its own chat history, example {'123': [], '456': []}

def load_docs():
    # Load the contents of the product catalog
    docs = []

    #loop through all the files in the directory
    for d in os.listdir(config.RAGSOURCES):
        path = os.path.join(config.RAGSOURCES, d)
        txtLoader = TextLoader(path)
        docs2 = txtLoader.load()
        docs.extend(docs2)

    return docs

def process_docs(docs):
    #chunk/split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    splits = text_splitter.split_documents(docs)
    return splits

def create_vectorstore(splits):
    #create embeddings from the splits and store in the vector store
    vectorStore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    return vectorStore

def create_document_chain(llm):
    #create the document chain from the llm and the prompt (which stores history)
    system_template = config.SYSTEM_TEMPLATE + """<context>{context}</context>"""
    
    question_answering_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_template,
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    document_chain = create_stuff_documents_chain(llm, question_answering_prompt)
    return document_chain

def create_retriever(vectorStore, k=config.TOP_K):
    #retrieve the top K relevant matches from the vector store
    retriever = vectorStore.as_retriever(k=k)
    return retriever

def create_my_history_aware_retriever(llm, retriever):
    #create a standalone question which can be understood without the chat history
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever

def create_rag_chain(history_aware_retriever, document_chain):
    rag_chain = create_retrieval_chain(history_aware_retriever, document_chain)
    return rag_chain

# def clear_history():
#     #clear the history
#     global my_chat_history
#     my_chat_history = []
#     if config.INFO_LOG:
#         print("History cleared!")

def clear_history(id):
    global chatHistory
    chatHistory.update({id: []})
    if config.INFO_LOG:
        print("History cleared!")

def cleanup(vector_store):
    #delete the collection
    vector_store.delete_collection()

# def query(rag_chain, q):
#     #pass the question and history to the rag chain and get the response
#     global my_chat_history

#     response = rag_chain.invoke({"input": q, "chat_history": my_chat_history})
#     my_chat_history.extend([HumanMessage(content=q), response["answer"]])
#     return response

def query(ragChain, q, id):
    global chatHistory
    if id not in chatHistory:
        chatHistory.update({id: []})

    myChatHistory = chatHistory[id]
    response = ragChain.invoke({"input": q, "chat_history": myChatHistory})
    myChatHistory.extend([HumanMessage(content=q), response["answer"]])
    return response

def create_json(answer):
    #create a json object from the answer
    answer = answer.replace('```', '').replace('\n', '').replace('json', '')

    try:
        structured_answer = json.loads(answer)
        was_json = True
    except Exception as e:
        was_json = False
        answer = "{" + answer + "}"
        try:
            structured_answer = json.loads(answer)
        except Exception as e:
            structured_answer = {"summary" : answer, "disclaimer" : config.DISCLAIMER}
            
    return structured_answer, was_json 

def print_context(response):
    #use this to understand the context (documents retrieved from vector store for a query)
    print("Context:")
    for document in response["context"]:
        print(document)

def initialize():
    global llm
    global chatHistory

    #load the docs, initialize the vector store and the rag chain
    print(config.GREETING)
    if config.SHOW_MODEL_INFO:
        print("Using model: {}".format(model))
    if config.INFO_LOG:
        print("Initializing...")
        print("Loading docs")
    docs = load_docs()
    if config.INFO_LOG:
        print("Done!")
        print("Processing docs")
    splits = process_docs(docs)
    if config.INFO_LOG:
        print("Creating vector store")
    vector_store = create_vectorstore(splits)
    if config.INFO_LOG:
        print("Creating retriever")
    retriever = create_retriever(vector_store, 10)
    if config.INFO_LOG:
        print("Creating history aware retriever")
    history_aware_retriever = create_my_history_aware_retriever(llm, retriever)
    if config.INFO_LOG:
        print("Creating document chain")
    document_chain = create_document_chain(llm)
    if config.INFO_LOG:
        print("Creating rag chain")
    rag_chain = create_rag_chain(history_aware_retriever, document_chain)
    if config.INFO_LOG:
        print("All done!")
    chatHistory = {} #each id has its own chat history, example {'123': [], '456': []}
    return rag_chain, vector_store

#main loop
if __name__ == '__main__':
    #used to store chat history for this user
    id=config.DEFAULT_USERID
    my_rag_chain, my_vector_store = initialize()
    status = True
    while status:
        q = input(config.USER_PROMPT)
        if q != "":
            if q.lower() == "clear":
                clear_history()
            elif q.lower() == "exit" or q.lower() == "bye" or q.lower() == "quit" or q.lower() == "end":
                status = False
            else:
                response = query(my_rag_chain, q, id)
                answer = response["answer"]
                print(answer)
                if config.SHOW_CONTEXT:
                    struct_answer, was_json = create_json(answer)
                    struct_answer["context"] = response["context"]
                    print(struct_answer)
        else:
            status = False
    if config.INFO_LOG:
        print("Cleaning up")
    cleanup(my_vector_store)