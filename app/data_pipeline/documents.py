from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path

@dataclass
class Document:
    id: str
    text: str
    metadata: Dict[str, str]
def load_text_files(root_dir: str, source_type: str) -> List[Document]:
    docs: List[Document] = []
    for path in Path(root_dir).rglob("*.txt"):
        if not path.is_file():
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        doc = Document(
            id=str(path),
            text=text,
            metadata={
                "source_type": source_type,
                "filename": path.name,
            },
        )
        docs.append(doc)
    return docs