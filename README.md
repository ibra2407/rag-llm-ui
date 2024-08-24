# Ollama RAG LLM with CustomTkinter UI
Running directly:
- Open up the project file and simply run app.py
  
Terminal commands:
- when adding a new document to "data", run the populate_database.py script; in terminal, "python populate_database.py"
- to run ollama server, "ollama serve" - this is required as Ollama runs a local server on http://127.0.0.1:11434/ that enables use of the LLMs
- to interact with the RAG LLM, in terminal, run 'python query_rag.py "{your prompt here}" '
-- e.g python query_rag.py "how do i get out of jail in monopoly?"

# References:
I referred to these amazing creators' work in my project. Much respect and many thanks to them for creating tutorials for everyone to learn from:

- Local RAG LLM: https://www.youtube.com/watch?v=2TJxpyO3ei4&t=66s (pixegami)
- Tkinter: https://www.youtube.com/watch?v=eoy9_S0sfP4 (b001)
