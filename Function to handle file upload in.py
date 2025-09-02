# Function to handle file upload in Colab
from google.colab import files

def upload_pdf():
    uploaded = files.upload()
    for filename in uploaded.keys():
        print(f'Uploaded {filename}')
        return filename
    return None

# Upload and process PDF
pdf_filename = upload_pdf()
if pdf_filename:
    with open(pdf_filename, 'rb') as f:
        chatbot.process_lecture_notes(f)
    print("Lecture notes processed successfully!")
else:
    print("No file uploaded.")