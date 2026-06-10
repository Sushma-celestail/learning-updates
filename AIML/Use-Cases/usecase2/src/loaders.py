import glob

from langchain_community.document_loaders import (
    PyPDFLoader,
    SitemapLoader
)


# LOAD PDF

def load_pdf(pdf_path):

    loader = PyPDFLoader(pdf_path)

    docs = loader.load()

    return docs


# LOAD FASTAPI HTML DOCS

def load_fastapi_docs():

    loader = SitemapLoader(
        web_path="https://fastapi.tiangolo.com/sitemap.xml"
    )

    docs = loader.load()

    for doc in docs:

        if "source" not in doc.metadata:

            doc.metadata["source"] = (
                "https://fastapi.tiangolo.com/"
            )

    return docs