import os
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Max token size (for example purposes, adjust as needed)
MAX_TOKENS = 8000  # Adjust this value based on your model's token limit


def sanitize_input(data):
    try:
        return data.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError:
        # Dacă există caractere nevalide, le eliminăm sau le înlocuim cu ceva valid
        return ''.join([char if ord(char) < 128 else ' ' for char in data])

def generate_text_in_fragments(prompt, data):
    token = os.environ["GITHUB_TOKEN"]="";
    endpoint = "https://models.inference.ai.azure.com"
    model_name = "gpt-4o"
    #model_name = "Llama-3.2-90B-Vision-Instruct"


    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )
    data = sanitize_input(data)  # Sanitizarea datelor înainte de procesare

    # Split data into smaller chunks based on MAX_TOKENS
    def chunk_data(data, max_tokens):
        chunks = []
        current_chunk = ""
        for line in data.splitlines():
            if len(current_chunk) + len(line) + 1 > max_tokens:
                chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += ("\n" + line) if current_chunk else line
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    chunks = chunk_data(data, MAX_TOKENS)
    full_response = ""

    # Send each chunk in a separate request
    for chunk in chunks:
        response = client.complete(
            stream=True,
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content=f"{prompt}\n {chunk}"),
            ],
            model=model_name,
        )
        for update in response:
            if update.choices:
                full_response += (update.choices[0].delta.content or "")

    client.close()
    return "Generated text based on: " + full_response


def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def read_pdf(file_path):
    reader = PdfReader(file_path)
    extracted_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text.append(text.encode("utf-8", "ignore").decode("utf-8", "ignore"))  # Ignoră caracterele problematice
    return "\n".join(extracted_text)



def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def read_excel(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')
    return df.to_string()


def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df.to_string()


def read_file(file_path):
    if not os.path.exists(file_path):
        return "Fișierul nu există!"

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        return read_txt(file_path)
    elif ext == ".pdf":
        return read_pdf(file_path)
    elif ext in [".doc", ".docx"]:
        return read_docx(file_path)
    elif ext in [".xls", ".xlsx"]:
        return read_excel(file_path)
    elif ext == ".csv":
        return read_csv(file_path)
    else:
        return "Format de fișier neacceptat!"


def read_folder(folder_path):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return "Folderul nu există sau nu este un director valid!"

    all_text = ""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):  # Verifică dacă este un fișier (nu un subfolder)
            file_content = read_file(file_path)
            all_text += f"\n--- Conținutul fișierului: {filename} ---\n{file_content}\n"

    return all_text


if __name__ == "__main__":
    file_path = input("Introduceți calea către fișier: ")
    print("\n--- Conținutul fișierului ---\n")
    file_content = read_file(file_path)  # Citește conținutul fișierului

    promtGPT = input("Scrie un text: ")
    print("Textul tău pentru GPT: ", promtGPT)

    # Folosește funcția generate_text pentru a genera text pe baza promptului și al conținutului fișierului
    text_generat = generate_text_in_fragments(promtGPT, file_content)  # Combinați promptul și conținutul fișierului
    print("\n--- Textul generat de GPT ---\n")
    print(text_generat)
    if __name__ == "__main__":
        path = input("Introduceți calea către fișier sau folder: ")

        if os.path.isdir(path):
            print("\n--- Conținutul folderului ---\n")
            content = read_folder(path)
        else:
            print("\n--- Conținutul fișierului ---\n")
            content = read_file(path)

        print(content)

        promtGPT = input("Scrie un text: ")
        print("Textul tău pentru GPT: ", promtGPT)

        text_generat = generate_text_in_fragments(promtGPT, content)
        print("\n--- Textul generat de GPT ---\n")
        print(text_generat)
