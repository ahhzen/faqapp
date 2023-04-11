from flask import Flask, render_template, request
from gpt_index import SimpleDirectoryReader, GPTListIndex, GPTSimpleVectorIndex, LLMPredictor, PromptHelper,  ServiceContext
from langchain import OpenAI
import sys
import os

app = Flask(__name__)
knowledgePath = os.getcwd() + '/knowledge'
indexPath = os.getcwd() + '/index'

knowledgeName = 'knowledge.json'
index = None

@app.route('/', methods=['GET', 'POST'])
def search():
    global index
    if index is None:
        "index not loaded yet. initializing..."
        index = init()

    if request.method == 'POST':
        query = request.form['question']
        # TODO: process query
        answer = answerQuestion(query)
        result = {'question': query, 'answer': answer}

        return render_template('search.html', result=result)
    else:
        return render_template('search.html')

def init():
    #Try to load existing index from disk - sourceIndexFile = os.getcwd() + '/index/' + knowledgeName
    
    sourceIndexFile = os.getcwd() + '/index/' + knowledgeName
    try:
        print("Loading index from disk...path: " + sourceIndexFile + "")
        index = GPTSimpleVectorIndex.load_from_disk(sourceIndexFile)
    except:
        print("Index not found. Creating new index...")
        index = createIndex()
    return index

def answerQuestion(query):
    print(f"Question: {query}")
    response = index.query(query, response_mode="compact")
    print(f"Answer: {response}")
    return response

def loadKnowledge():
    #knowledgePath = os.getcwd() + '/knowledge' 
    print("Loading TXT knowledge from disk...path: " + knowledgePath + "")
    return SimpleDirectoryReader(knowledgePath).load_data()

def createIndex():
    max_input = 4096
    tokens = 256
    chunk_size = 600
    max_chunk_overlap = 20

    docs = loadKnowledge()

    # Get the API key from the environment variable
    # openai_api_key = os.environ.get("OPENAI_API_KEY")
    api_key = os.environ.get("OPENAI_API_KEY")

    llmPredictor = LLMPredictor(llm=OpenAI(api_key=api_key, temperature=0, model_name="text-davinci-003", max_tokens=tokens)) 
    service_context = ServiceContext.from_defaults(llm_predictor=llmPredictor, chunk_size_limit=chunk_size)
    vectorIndex = GPTSimpleVectorIndex.from_documents(docs, service_context=service_context)

    targetIndexFile = os.getcwd() + '/index/' + knowledgeName
    vectorIndex.save_to_disk(targetIndexFile)
    print("Index saved to disk. path: " + targetIndexFile + "")

    return vectorIndex


if __name__ == '__main__':
    #run app in production on port 5005
    app.run(host='0.0.0.0', port=5005)
    # app.run(host='0.0.0.0', port=5005, debug=False)