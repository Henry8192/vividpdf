from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import json

data = []

for page_layout in extract_pages("test.pdf"):
    page_info = {"page_number": page_layout.pageid, "elements": []}
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                line_info = {
                    "text": text_line.get_text().strip(),
                    "x0": text_line.x0,
                    "y0": text_line.y0,
                    "x1": text_line.x1,
                    "y1": text_line.y1,
                    "chars": []
                }
                for char in text_line:
                    if isinstance(char, LTChar):
                        line_info["chars"].append({
                            "char": char.get_text(),
                            "x0": char.x0,
                            "y0": char.y0,
                            "size": char.size,
                            "font": char.fontname
                        })
                page_info["elements"].append(line_info)
    data.append(page_info)

with open("test_PDFMiner_detailed.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
