from flask import Flask, render_template, request, session
import uuid
from gpt_index import SimpleDirectoryReader, GPTListIndex, GPTSimpleVectorIndex, LLMPredictor, PromptHelper,  ServiceContext
from langchain import OpenAI
import openai
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
    print(f"HTTP request received from {request.remote_addr} - {getUniqueName()}")
    if index is None:
        "index not loaded yet. initializing..."
        index = init()
    
    if index is None:
        return render_template('search.html', result={'question': 'Error: index not loaded yet'})

    if request.method == 'POST':
        query = request.form['question']

        answer = answerQuestion(query)
        result = {'question': query, 'answer': answer}

        return render_template('search.html', result=result)
    else:
        return render_template('search.html')

def getUniqueName():
    return str(uuid.uuid4())
    

def is_valid_api_key():
    # Replace YOUR_API_KEY with your actual OpenAI API key
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    try:
        # Send a test request to the API
        response = openai.Completion.create(
            engine="davinci",
            prompt="Hello, World!",
            max_tokens=2
            )
    except:
        return False

    # Return True if len more than 0
    if len(response.choices[0].text) > 0:
        return True

def init():
    l_index = None
    #Try to load existing index from disk - sourceIndexFile = os.getcwd() + '/index/' + knowledgeName
    sourceIndexFile = os.getcwd() + '/index/' + knowledgeName
    try:
        print("Loading index from disk...path: " + sourceIndexFile + "")
        l_index = GPTSimpleVectorIndex.load_from_disk(sourceIndexFile)
    except:
        print("Existing index not found in '/index'. Creating new index...")
        l_index = createIndex()
    return l_index

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

    #Check API key is valid otherwise exit function
    if not is_valid_api_key():
        print("Invalid API key")
        return

    docs = loadKnowledge()

    # Get the API key from the environment variable
    api_key = os.environ.get("OPENAI_API_KEY")

    llmPredictor = LLMPredictor(llm=OpenAI(api_key=api_key, temperature=0, model_name="text-davinci-003", max_tokens=tokens)) 
    service_context = ServiceContext.from_defaults(llm_predictor=llmPredictor, chunk_size_limit=chunk_size)
    vectorIndex = GPTSimpleVectorIndex.from_documents(docs, service_context=service_context)

    #Save index to disk - /index/knowledge.json
    targetIndexFile = os.getcwd() + '/index/' + knowledgeName
    vectorIndex.save_to_disk(targetIndexFile)
    print("Index saved to disk. path: " + targetIndexFile + "")

    return vectorIndex


if __name__ == '__main__':
    #run app in production on port 5005
    app.run(host='0.0.0.0', port=5005)
    # app.run(host='0.0.0.0', port=5005, debug=False)