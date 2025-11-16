# 垃圾 

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno
import json
import os

def pdf_to_html_or_json(pdf_path, output_format="html", output_file=None):
    """
    Convert a PDF file to HTML or JSON, preserving font styles and formatting.
    
    Args:
        pdf_path (str): Path to the PDF file.
        output_format (str): 'html' or 'json'
        output_file (str, optional): Path to save output file.
    """
    pages_data = []

    for page_layout in extract_pages(pdf_path):
        page_items = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    line_data = []
                    for character in text_line:
                        if isinstance(character, LTChar):
                            char_data = {
                                "text": character.get_text(),
                                "fontname": character.fontname,
                                "size": character.size,
                                "bold": "Bold" in character.fontname,
                                "italic": "Italic" in character.fontname or "Oblique" in character.fontname,
                                "x": character.x0,
                                "y": character.y0
                            }
                            line_data.append(char_data)
                        elif isinstance(character, LTAnno):
                            # Whitespace or linebreak
                            line_data.append({"text": character.get_text()})
                    page_items.append(line_data)
        pages_data.append(page_items)

    # --- Output as JSON ---
    if output_format.lower() == "json":
        result = json.dumps(pages_data, indent=2)
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
        return result

    # --- Output as HTML ---
    elif output_format.lower() == "html":
        html_output = "<html><body>"
        for page in pages_data:
            html_output += '<div class="page">'
            for line in page:
                html_output += "<p>"
                for char in line:
                    if "text" not in char:
                        continue
                    style = ""
                    if char.get("bold"):
                        style += "font-weight:bold;"
                    if char.get("italic"):
                        style += "font-style:italic;"
                    if char.get("size"):
                        style += f"font-size:{char['size']}px;"
                    html_output += f'<span style="{style}">{char["text"]}</span>'
                html_output += "</p>"
            html_output += "</div>"
        html_output += "</body></html>"

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_output)
        return html_output

    else:
        raise ValueError("output_format must be 'html' or 'json'.")

# Example usage:
html_output = pdf_to_html_or_json("calculus_textbook.pdf", "html", "output.html")
json_output = pdf_to_html_or_json("test.pdf", "json", "output.json")

