import os
import uuid
import tempfile
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from pdf_processor import convert_pdf_to_html

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['TEMP_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    assert isinstance(filename, str), "Filename must be a string"
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_temp_filename():
    """Generate a unique temporary filename."""
    assert isinstance(uuid.uuid4(), uuid.UUID), "UUID generation failed"
    return str(uuid.uuid4())

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload."""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_id = generate_temp_filename()
            temp_path = os.path.join(app.config['TEMP_FOLDER'], temp_id + ".pdf")
            
            file.save(temp_path)
            session['temp_pdf_path'] = temp_path
            
            return redirect(url_for('edit_pdf', temp_id=temp_id))
    
    return render_template('index.html')

@app.route('/edit/<temp_id>', methods=['GET'])
def edit_pdf(temp_id):
    """Render the edit page with converted PDF."""
    assert isinstance(temp_id, str), "Temp ID must be a string"
    
    temp_path = session.get('temp_pdf_path')
    if not temp_path or not os.path.exists(temp_path):
        return redirect(url_for('upload_file'))
    
    try:
        html_content = convert_pdf_to_html(temp_path)
        assert isinstance(html_content, str), "HTML content must be a string"
        
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            session.pop('temp_pdf_path', None)
        
        return render_template('edit.html', html_content=html_content)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            session.pop('temp_pdf_path', None)
        return f"Error processing PDF: {str(e)}"

@app.route('/save', methods=['POST'])
def save_edited_content():
    """Handle saving edited content (optional download)."""
    edited_content = request.form.get('content', '')
    assert isinstance(edited_content, str), "Edited content must be a string"
    
    # Here you could implement logic to convert HTML back to PDF
    # For now, we'll just return a success message
    return "Content saved successfully!"

if __name__ == '__main__':
    app.run(debug=True)
