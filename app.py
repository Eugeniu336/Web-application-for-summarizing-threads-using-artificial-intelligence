import sys
import os
import streamlit as st
from main import read_file, generate_text_in_fragments


def process_folder(folder_path):
    """Procesează toate fișierele din folder."""
    all_text = ""
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_content = read_file(file_path)
            all_text += f"\n--- {file} ---\n{file_content}\n"
    return all_text


def main():
    st.title("Analiză AI a Folderului")

    folder_path = None
    if len(sys.argv) > 1:  # Primește folderul de analizat ca argument
        folder_path = sys.argv[1]

    if folder_path and os.path.isdir(folder_path):
        st.write(f"Analizăm folderul: `{folder_path}`")
        text_content = process_folder(folder_path)
        prompt = st.text_area("Introduceți promptul pentru AI:")

        if prompt and st.button("Generează analiza"):
            with st.spinner("Se procesează..."):
                generated_text = generate_text_in_fragments(prompt, text_content)
            st.subheader("Rezultatul:")
            st.text_area("", generated_text, height=300)
    else:
        st.error("Nu a fost specificat un folder valid.")


if __name__ == "__main__":
    main()

#app script google
#asistent inteligenr
