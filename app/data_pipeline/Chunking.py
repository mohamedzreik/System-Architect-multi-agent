from dataclasses import dataclass
from typing import Dict, List

from .documents import Document


@dataclass
class Chunk:
    id: str
    text: str
    metadata: Dict[str, str]


def simple_chunk_document(
        doc: Document,
        max_chars: int = 1000,
        overlap: int = 200,
) -> List[Chunk]:
    text = doc.text
    chunks: List[Chunk] = []

    # Split by paragraphs first
    paragraphs = [p for p in text.split('\n\n') if p.strip()]

    current_chunk = []
    current_length = 0
    chunk_index = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph would exceed max_chars, finalize current chunk
        if current_length + len(para) > max_chars and current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunk_id = f"{doc.id}::chunk{chunk_index}"
            metadata = dict(doc.metadata)
            metadata["chunk_index"] = str(chunk_index)

            chunks.append(
                Chunk(
                    id=chunk_id,
                    text=chunk_text,
                    metadata=metadata,
                )
            )

            chunk_index += 1

            # Keep overlap by carrying over last paragraph(s)
            overlap_text = []
            overlap_length = 0
            for para_backwards in reversed(current_chunk):
                if overlap_length + len(para_backwards) <= overlap:
                    overlap_text.insert(0, para_backwards)
                    overlap_length += len(para_backwards)
                else:
                    break

            current_chunk = overlap_text
            current_length = overlap_length

        # Add paragraph to current chunk
        current_chunk.append(para)
        current_length += len(para)

    # Don't forget the last chunk
    if current_chunk:
        chunk_text = '\n\n'.join(current_chunk)
        chunk_id = f"{doc.id}::chunk{chunk_index}"
        metadata = dict(doc.metadata)
        metadata["chunk_index"] = str(chunk_index)

        chunks.append(
            Chunk(
                id=chunk_id,
                text=chunk_text,
                metadata=metadata,
            )
        )

    return chunks

def chunk_documents(
    docs: List[Document],
    max_chars: int = 1000,
    overlap: int = 200,
) -> List[Chunk]:

    all_chunks: List[Chunk] = []

    for doc in docs:
        doc_chunks = simple_chunk_document(doc, max_chars=max_chars, overlap=overlap)
        all_chunks.extend(doc_chunks)

    return all_chunks