import pdfplumber

print("Converting PDF to text...")

with pdfplumber.open("sauravkumar.pdf") as pdf:
    resume_text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            resume_text += page_text

with open("sauravkumar.txt", "w", encoding="utf-8") as f:
    f.write(resume_text)

print("Resume text saved to sauravkumar.txt")
