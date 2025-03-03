import pdfplumber
import re

def convert_pdf_to_html(pdf_path):
    """
    Convert PDF to HTML preserving formatting.
    
    Args:
        pdf_path (str): Path to PDF file
        
    Returns:
        str: HTML content
    """
    assert isinstance(pdf_path, str), "PDF path must be a string"
    assert pdf_path.endswith(".pdf"), "File must be a PDF"
    
    html_parts = ["<!DOCTYPE html><html><body>"]
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            assert page_count > 0, "PDF has no pages"
            
            # Process each page, with a fixed upper bound
            for page_num in range(min(page_count, 1000)):  # Limit to 1000 pages max
                page = pdf.pages[page_num]
                
                html_parts.append(f'<div class="page" id="page-{page_num+1}">')
                
                # Extract text with formatting information
                words = page.extract_words(x_tolerance=3, y_tolerance=3, keep_blank_chars=True)
                
                # Group words by their y-position (lines)
                lines = {}
                for word in words:
                    y_pos = int(word['top'])
                    if y_pos not in lines:
                        lines[y_pos] = []
                    lines[y_pos].append(word)
                
                # Sort lines by y-position
                sorted_lines = sorted(lines.items())
                
                # Process each line (up to a limit)
                line_count = len(sorted_lines)
                for line_idx in range(min(line_count, 200)):
                    if line_idx >= len(sorted_lines):
                        break
                        
                    y_pos, line_words = sorted_lines[line_idx]
                    
                    # Sort words in the line by x-position
                    line_words.sort(key=lambda w: w['x0'])
                    
                    line_html = []
                    for word in line_words:
                        text = word['text']
                        
                        # Sanitize text for HTML
                        text = sanitize_html_text(text)
                        
                        # Extract some basic font size info from word height
                        font_size = max(int(word['height'] * 0.8), 10)
                        
                        # Create styled span
                        style = f"font-size:{font_size}px;"
                        line_html.append(f'<span style="{style}">{text} </span>')
                    
                    html_parts.append(f'<div class="line">{" ".join(line_html)}</div>')
                
                html_parts.append('</div>')
        
    except Exception as e:
        html_parts.append(f'<p>Error processing PDF: {str(e)}</p>')
    
    html_parts.append("</body></html>")
    return "".join(html_parts)

def sanitize_html_text(text):
    """
    Sanitize text for safe HTML rendering.
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    assert isinstance(text, str), "Text must be a string"
    
    # Replace special HTML characters
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#39;")
    
    return text
