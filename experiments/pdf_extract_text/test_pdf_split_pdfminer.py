from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTChar, LTTextLineHorizontal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def split_pdf_sentences(input_pdf):
    sentences = []
    sentence_metadata = []
    
    # Extract layout info
    for page_layout in extract_pages(input_pdf):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                for line in element:
                    if isinstance(line, LTTextLineHorizontal):
                        text = line.get_text().strip()
                        if not text:
                            continue
                        # Split by period but keep positions
                        parts = text.split('.')
                        for i, part in enumerate(parts):
                            part = part.strip()
                            if part:
                                sentences.append(part + ('.' if i < len(parts) - 1 else ''))
                                sentence_metadata.append({
                                    "x0": line.x0,
                                    "y0": line.y0,
                                    "page_height": page_layout.bbox[3],
                                    "font_size": None,
                                    "color": None
                                })
    return sentences, sentence_metadata

def generate_sentence_pdfs(sentences, metadata, output_folder="output_pdfs"):
    os.makedirs(output_folder, exist_ok=True)
    
    for i, sentence in enumerate(sentences):
        meta = metadata[i]
        filename = os.path.join(output_folder, f"sentence_{i+1}.pdf")
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Position text based on extracted coordinates
        x = meta["x0"]
        y = meta["page_height"] - meta["y0"]  # convert PDFMiner to ReportLab coords
        c.setFont("Helvetica", 12)
        c.drawString(x, y, sentence)
        
        c.save()

def main():
    input_pdf = "test.pdf"
    sentences, metadata = split_pdf_sentences(input_pdf)
    generate_sentence_pdfs(sentences, metadata)
    print(f"Generated {len(sentences)} PDFs in 'output_pdfs/'")

if __name__ == "__main__":
    main()
