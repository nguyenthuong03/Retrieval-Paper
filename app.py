import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from llm_handler import LLMHandler

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize components
pdf_processor = PDFProcessor()
vector_store = VectorStore()
llm_handler = LLMHandler()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process PDF and add to vector store
        chunks = pdf_processor.process_pdf(filepath)
        vector_store.add_texts(chunks)
        
        return jsonify({'message': 'File uploaded and processed successfully'})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    if not data or 'question' not in data:
        return jsonify({'error': 'No question provided'}), 400
    
    question = data['question']
    
    # Retrieve relevant context
    context = vector_store.similarity_search(question)
    
    # Generate response
    response = llm_handler.generate_response(question, context)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    # Run the app on all available interfaces
    app.run(host='0.0.0.0', port=port, debug=False) 