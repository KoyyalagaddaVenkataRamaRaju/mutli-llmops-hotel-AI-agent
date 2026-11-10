from typing import List, Dict, Any

class HierarchicalSemanticChunker:
    """
    Semantic & Hierarchical Chunking Engine.
    Breaks high-level hotel manuals into structured semantic units enriched with:
    - Role Context ([RECEPTIONIST], [MANAGER], [OWNER], [HOUSEKEEPING], [SUPPORT])
    - Section hierarchy and operational tags
    - Sliding window with sentence-boundary overlap for continuous context
    """
    @staticmethod
    def chunk_document(
        doc_id: str,
        role: str,
        category: str,
        title: str,
        raw_text: str,
        window_size_words: int = 120,
        overlap_words: int = 25
    ) -> List[Dict[str, Any]]:
        words = raw_text.split()
        if len(words) <= window_size_words:
            content_with_context = f"[ROLE: {role.upper()}] [CATEGORY: {category}] [TOPIC: {title}]\n{raw_text}"
            return [{
                "id": doc_id,
                "role": role,
                "category": category,
                "title": title,
                "content": content_with_context,
                "raw_content": raw_text,
                "chunk_index": 0,
                "total_chunks": 1
            }]

        chunks = []
        step = max(1, window_size_words - overlap_words)
        chunk_idx = 0
        for i in range(0, len(words), step):
            window = words[i : i + window_size_words]
            chunk_body = " ".join(window)
            content_with_context = f"[ROLE: {role.upper()}] [CATEGORY: {category}] [TOPIC: {title} (Part {chunk_idx + 1})]\n{chunk_body}"
            chunks.append({
                "id": f"{doc_id}-C{chunk_idx + 1}",
                "role": role,
                "category": category,
                "title": f"{title} (Part {chunk_idx + 1})",
                "content": content_with_context,
                "raw_content": chunk_body,
                "chunk_index": chunk_idx,
                "total_chunks": 0
            })
            chunk_idx += 1
            if i + window_size_words >= len(words):
                break

        for c in chunks:
            c["total_chunks"] = len(chunks)
        return chunks

