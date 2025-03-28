from typing import List
import os
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def process_pdf(self, pdf_path: str) -> List[str]:
        """Process a PDF file and return chunks of text."""
        text = self.extract_text_from_pdf(pdf_path)
        chunks = self.text_splitter.split_text(text)
        return chunks

    def process_directory(self, directory_path: str) -> List[str]:
        """Process all PDF files in a directory."""
        all_chunks = []
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(directory_path, filename)
                chunks = self.process_pdf(pdf_path)
                all_chunks.extend(chunks)
        return all_chunks 