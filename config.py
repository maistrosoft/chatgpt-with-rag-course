MODEL = "gpt-4o-mini"
#model = "gpt-3.5-turbo-0125"
TEMPERATURE = 0.2

RAGSOURCES = "ragsources"

GREETING = """Hello, I'm the ShoeRack chatbot.
POST your queries at /api/query.
Clear history at /api/query/clear"""

DEFAULT_PORT = "8000"
DEFAULT_USERID = "12345"

SHOW_MODEL_INFO = True
INFO_LOG = True
DEBUG_LOG = False
SHOW_CONTEXT = False
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

SYSTEM_TEMPLATE = """
You are a customer assistant who can answer questions about products in The Shoe Rack, a large online store
selling shoes and sandals for men, women and children.
Be courteous and only answer questions that are relevant to the context given below.
Remove the prices of products from the answer.
Only when the question is specifically on price or cost, include the prices of the products in the answer.
If you cannot answer the question based on the context,
just say 'I'm sorry, I I don't know. Would you like to speak to a human agent?'.
Don't make something up.
"""
TOP_K = 10

DISCLAIMER = "As an AI model, I can be occasionally wrong or incomplete in my answers. Kindly check with human experts if you are unsure about the answer."

USER_PROMPT = """How can I help you?
To clear history, enter 'clear'
To exit enter 'bye' or 'exit' or just press enter
Enter your query:"""


# Model Name, text, length 50
# Temperature, text, length 5
# Rag Source Folder, text, length 50
# Greeting: multi line text, 5 lines, each length 80
# Default port, text, Length 5
# Default User ID, text, Length 25
# Show model information, radio button, true, false
# Information log, radio button, true, false
# Debug log, radio button, true, false
# Show context, radio button, true, false
# Chunk size, text, 10
# Chunk overlap, text, 10
# System template, multi line text, 25 lines each length 80
# Top K, text, 10
# Disclaimer, multi line text, 2 lines, each length 80
# User prompt, multi line text, 5 lines, each length 80