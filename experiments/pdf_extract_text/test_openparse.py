import openparse

basic_doc_path = "test.pdf"
parser = openparse.DocumentParser()
parsed_basic_doc = parser.parse(basic_doc_path)

for node in parsed_basic_doc.nodes:
    print(node)
    print()

print(parsed_basic_doc.json())
