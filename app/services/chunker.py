from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text: str, doc_name: str, doc_type: str) -> list[dict]:
    """
    Split text into chunks with metadata.
    doc_type: 'regulation' or 'policy'
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(text)
    return [
        {
            "text": chunk,
            "metadata": {
                "doc_name": doc_name,
                "doc_type": doc_type,
                "chunk_index": i
            }
        }
        for i, chunk in enumerate(chunks)
    ]
