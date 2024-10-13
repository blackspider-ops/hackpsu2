from flask import Flask, render_template, request, jsonify
import json
from openai import OpenAI

app = Flask(__name__)

# Initialize the OpenAI client with your API key
client = OpenAI(api_key="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")

# Load the ICDS data from the JSON file
icds_data = json.load(open('icds_guide_data.json'))

# Step 1: Load the scraped data from the JSON file (no change needed)
def load_icds_data(file_path):
    with open(file_path, 'r') as file:
        icds_data = json.load(file)
    return icds_data

# Step 2: Retrieve the most relevant section based on the user's question
def retrieve_relevant_section(question, data):
    relevant_sections = []
    for section in data:
        if any(word.lower() in section['content'].lower() for word in question.split()):
            relevant_sections.append(section)
    
    if not relevant_sections:
        return "No relevant section found. Please try a different question."
    
    return relevant_sections

# Step 3: OpenAI Chatbot Integration
def generate_response(question, client, icds_data):
    relevant_sections = retrieve_relevant_section(question, icds_data)
    
    if isinstance(relevant_sections, str):
        return relevant_sections
    
    relevant_content = "\n\n".join([f"Title: {section['title']}\nContent: {section['content']}" for section in relevant_sections])

    prompt = f"Based on the following ICDS documentation, summarize the answer to the user's question: {question}\n\n{relevant_content}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )
    
    return response.choices[0].message.content

# Flask Routes

# Serve the HTML file
@app.route('/')
def index():
    return render_template('index.html')  # This will point to your HTML file

# Handle chat requests
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'response': 'Invalid input'}), 400
    
    # Generate a response using the chatbot logic
    response = generate_response(user_input, client, icds_data)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
