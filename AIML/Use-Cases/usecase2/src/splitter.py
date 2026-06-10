from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

def split_docs(documents):

    return text_splitter.split_documents(documents)