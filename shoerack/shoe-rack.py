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
import pprint

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
#model = "gpt-3.5-turbo-0125"
model = "gpt-4o-mini"
temperature = 0.2
llm = ChatOpenAI(model=model, temperature=temperature)
my_chat_history = []

def load_docs():
    # Load the contents of the product catalog
    docs = []

    #loop through all the files in the directory
    for d in os.listdir("ragsources"):
        path = os.path.join("ragsources", d)
        txtLoader = TextLoader(path)
        docs2 = txtLoader.load()
        docs.extend(docs2)

    return docs

def process_docs(docs):
    #chunk/split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    return splits

def create_vectorstore(splits):
    #create embeddings from the splits and store in the vector store
    vectorStore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    return vectorStore

def create_document_chain(llm):
    #create the document chain from the llm and the prompt (which stores history)
    SYSTEM_TEMPLATE = """
    You are a customer assistant who can answer questions about products in The Shoe Rack, a large online store
    selling shoes and sandals for men, women and children.
    You are given a context below.
    Answer the user's questions based on the below context. 
    <context>
        {context}
    </context>
    Be courteous and only answer questions that are relevant to the context.
    When providing summary or recommendations, include only the product name and description.
    Only when the question is on price or cost, include the price.
    If the context doesn't contain any relevant information to the question,
    just say 'I'm sorry, I I don't know. Would you like to speak to a human agent?'.
    Don't make something up.
    """
    
    question_answering_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SYSTEM_TEMPLATE,
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    document_chain = create_stuff_documents_chain(llm, question_answering_prompt)
    return document_chain

def create_retriever(vectorStore, k=10):
    #retrieve the top K relevant matches from the vector store
    retriever = vectorStore.as_retriever(k=10)
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

def clear_history():
    #clear the history
    global my_chat_history
    my_chat_history = []
    print("History cleared!")

def cleanup(vector_store):
    #delete the collection
    vector_store.delete_collection()

def query(rag_chain, q):
    #pass the question and history to the rag chain and get the response
    global my_chat_history

    response = rag_chain.invoke({"input": q, "chat_history": my_chat_history})
    my_chat_history.extend([HumanMessage(content=q), response["answer"]])
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
            structured_answer = {"summary" : answer, "disclaimer" : "As an AI model, I can be occasionally wrong or incomplete in my answers. Kindly check with human experts if you are unsure about the answer."}
            
    return structured_answer, was_json 

def print_context(response):
    #use this to understand the context (documents retrieved from vector store for a query)
    print("Context:")
    for document in response["context"]:
        print(document)

def initialize():
    #load the docs, initialize the vector store and the rag chain
    global llm
    print("Loading docs")
    docs = load_docs()
    print("Processing docs")
    splits = process_docs(docs)
    print("Creating vector store")
    vector_store = create_vectorstore(splits)
    retriever = create_retriever(vector_store, 10)
    history_aware_retriever = create_my_history_aware_retriever(llm, retriever)
    document_chain = create_document_chain(llm)
    rag_chain = create_rag_chain(history_aware_retriever, document_chain)
    return rag_chain, vector_store

#main loop
if __name__ == '__main__':
    print("Welcome to The Shoes Rack RAG Chatbot demo. Using model: {}".format(model))
    my_rag_chain, my_vector_store = initialize()
    status = True
    while status:
        q = input("How can I help you?\n---- To clear history, enter 'clear'\n---- To exit enter 'bye' or 'exit' or just press enter\nEnter your query:")
        if q != "":
            if q.lower() == "clear":
                clear_history()
            elif q.lower() == "exit" or q.lower() == "bye" or q.lower() == "quit" or q.lower() == "end":
                status = False
            else:
                response = query(my_rag_chain, q)
                answer = response["answer"]
                print(answer)
                #struct_answer, was_json = create_json(answer)
                #struct_answer["context"] = response["context"]
                #print(struct_answer)
        else:
            status = False
    print("Cleaning up")
    cleanup(my_vector_store)