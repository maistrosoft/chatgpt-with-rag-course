from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import vector_store_rag_history as vsrh
import config

app = Flask(__name__)

myRagChain = None
myVectorStore = None

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

@app.route("/", methods=["GET"])
def index():
    return config.GREETING

@app.route('/settings')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    data = {
        "Model Name": request.form.get('model_name'),
        "Temperature": request.form.get('temperature'),
        "Rag Source Folder": request.form.get('rag_source_folder'),
        "Greeting": request.form.get('greeting'),
        "Default port": request.form.get('default_port'),
        "Default User ID": request.form.get('default_user_id'),
        "Show model information": request.form.get('show_model_information'),
        "Information log": request.form.get('information_log'),
        "Debug log": request.form.get('debug_log'),
        "Show context": request.form.get('show_context'),
        "Chunk size": request.form.get('chunk_size'),
        "Chunk overlap": request.form.get('chunk_overlap'),
        "System template": request.form.get('system_template'),
        "Top K": request.form.get('top_k'),
        "Disclaimer": request.form.get('disclaimer'),
        "User prompt": request.form.get('user_prompt'),
    }

    # Validate Temperature
    try:
        temperature = float(data["Temperature"])
        if not (0 <= temperature <= 10):
            raise ValueError
    except ValueError:
        flash("Temperature must be a real number between 0 and 10")
        return redirect(url_for('form'))

    # Validate numeric fields
    numeric_fields = ["Default port", "Chunk size", "Chunk overlap", "Top K"]
    for field in numeric_fields:
        try:
            int(data[field])
        except ValueError:
            flash(f"{field} must be a number")
            return redirect(url_for('form'))
    
    # Save data to file
    with open('data/submissions.txt', 'a') as f:
        for key, value in data.items():
            f.write(f"{key}: {value}\n")
        f.write("\n")
    
    return redirect(url_for('form'))

@app.route("/api/query", methods=["POST"])
def query_endpoint():
    global myRagChain, myVectorStore

    # Initialize the RAG chain and vector store if they are not already initialized
    if myRagChain is None:
        myRagChain, myVectorStore = vsrh.initialize()

    # Get the query from the request
    data = request.get_json()
    q = data.get("query")
    id = data.get("id") 

    #print("id: {}, query: {}".format(id, q))

    if q != "":
        # Process the query (you can replace this with your actual logic)
        response = process_query(q, id)
        print("response: {}".format(response))

        answer = response["answer"]
        #print("answer: {}".format(answer))

        # Return the response
        return jsonify({"response": answer})
    else:
        return jsonify({"response": "No query provided"})
    
@app.route("/api/query/clear", methods=["POST"])
def clear_history_endpoint():
    data = request.get_json()
    id = data.get("id") 
    vsrh.clear_history(id)
    return jsonify({"response": "History cleared"})

@app.route("/api/query/cleanup", methods=["POST"])
def cleanup():
    global myRagChain, myVectorStore
    data = request.get_json()
    id = data.get("id") 
    vsrh.clear_history(id)
    if myRagChain is not None:
        myRagChain = None
    if myVectorStore is not None:
        myVectorStore = None
    return jsonify({"response": "Cleanup completed"})

def process_query(query, id):
    global myRagChain
    response = vsrh.query(myRagChain, query, id)
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.DEFAULT_PORT, debug=True)
