from PyPDF2 import PdfReader
import json

# open the pdf
reader = PdfReader("test.pdf")

# extract text from each page
data = {"pages": []}
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    data["pages"].append({"page": i + 1, "text": text})

# save as json
with open("test_pypdf.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
