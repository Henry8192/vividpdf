from pdf_extract_kit import PDFExtractor

# Create extractor with layout parsing enabled
extractor = PDFExtractor("test.pdf")

# Extract structured data (with positions, fonts, sizes, etc.)
layout_data = extractor.extract_text(
    mode="layout",
    as_dict=True,
    include_bbox=True,         # Include bounding box coordinates
    include_font=True,         # Include font name and size
    include_style=True,        # Include bold/italic info if available
)

# Save it as JSON
extractor.to_json("test_PDF-Extract-Kit.json", layout_data)

print("Layout extraction complete: text with position and style saved.")
