import docx

def parse_docx(file) -> str:
    doc = docx.Document(file)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return text