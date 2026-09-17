import pypdf
import docx
import io

def extract_text(file_obj, input_kind: str) -> str:
    text = ""
    if input_kind == 'pdf':
        try:
            reader = pypdf.PdfReader(file_obj)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception:
            pass
    elif input_kind == 'docx':
        try:
            doc = docx.Document(file_obj)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception:
            pass
    return text.strip()
