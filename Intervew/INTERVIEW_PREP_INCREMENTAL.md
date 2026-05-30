# Interview Guide: Incremental Updates (The "Secret Sauce")

If an interviewer asks, **"How do you handle new or updated data in your RAG system? Do you re-run the whole pipeline?"**, you can impress them by explaining your **Incremental Update Mechanism**.

---

## 1. The Problem with Standard RAG
"In many basic RAG projects, if one page on the university website changes, you have to re-scrape everything and re-calculate embeddings for thousands of documents. This is slow and expensive (waste of API credits/compute)."

## 2. Your Solution: The Manifest System
"I built an **Incremental Update System** using a custom **Manifest**. Here is the technical logic:"

### A. The Manifest (The "Map")
- "I maintain a `manifest.json` file that maps every source file (e.g., `admissions.txt`) to the specific **Chunk IDs** it generated in the vector store."

### B. The "Remove-and-Replace" Workflow
"When I run `python main.py update <file_path>`, the system does three things atomically:"
1. **Lookup & Clean**: It looks into the manifest, finds all the old Chunk IDs for that file, and **removes** them from both the FAISS index and the metadata dictionary.
2. **Re-Process**: It re-scrapes/re-reads only that specific file, chunks it, and generates fresh embeddings.
3. **Inject**: It adds the new chunks back into the FAISS index and updates the manifest with the new IDs.

---

## 3. Why this is "Production-Grade"
Explain the benefits to show you're thinking like a Software Engineer:
- **Efficiency**: "We only process what changed. If the 'Fees' page updates, we don't touch the 'Library' page data."
- **Atomic Updates**: "The vector store stays consistent because we remove the old data before adding the new ones."
- **Scalability**: "This allows the system to scale to thousands of documents without the update time growing exponentially."

---

## 4. Key Code Terms to Mention:
- **`faiss.IndexIDMap`**: "I used this to allow deleting specific chunks by their ID, which is not possible in a standard Flat index."
- **`manifest.json`**: "The source-of-truth mapping between files and their vector representation."
- **`next_chunk_id`**: "A global counter to ensure every new chunk gets a unique identifier."

---

## 5. Sample Question: "What if a file is deleted?"
> *"I can extend the logic to detect when a file no longer exists in the 'extracted_text' folder, look up its IDs in the manifest, and purge them from the system completely, keeping the search results clean."*
