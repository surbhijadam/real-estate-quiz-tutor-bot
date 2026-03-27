# Real Estate Quiz & Tutor AI (Generative AI Project)

## Project Information
Division: D9  
Group Name: Group07D9  
Project No: GAI-07  

## Project Description
Real Estate Quiz & Tutor AI is a Generative AI based application designed to help users learn real estate concepts interactively. The system allows users to ask questions and also generate quizzes based on real estate training documents.

The project uses Retrieval Augmented Generation (RAG) where documents are converted into embeddings and stored in a vector database. When a user asks a question, the system retrieves the most relevant information and generates a response using an AI model.

## Technologies Used
- Python
- Streamlit (Frontend)
- Google Gemini API
- FAISS (Vector Database)
- Embeddings
- Retrieval Augmented Generation (RAG)

## Features
- AI Tutor for Real Estate Questions
- Automatic Quiz Generation
- Document-based Question Answering
- Fast semantic search using vector embeddings
- Interactive web interface

## Project Workflow
1. Real estate documents are stored in the data folder.
2. The documents are processed and converted into embeddings.
3. Embeddings are stored in a vector database.
4. When the user asks a question, the system retrieves relevant information.
5. The AI model generates a response.
6. The quiz generator creates questions based on the document content.

## Project Structure

```
REAL-ESTATE-QUIZ/
│
├── data/
│   └── real_estate_docs.txt
│
├── app.py
├── embeddings.py
├── vector_db.py
├── quiz_generator.py
├── tutor_chat.py
├── cache_manager.py
├── fallback_questions.py
│
├── requirements.txt
├── .gitignore
│
└── backup files
    ├── quiz_generator_backup.py
    └── tutor_chat_backup.py
```

## Installation

Clone the repository

```
git clone https://github.com/your-repository-link
```

Install dependencies

```
pip install -r requirements.txt
```

Run the application

```
streamlit run app.py
```

## Future Improvements
- Add voice-based learning
- Improve quiz difficulty levels
- Add more real estate training datasets
- Improve UI design

## Authors
Generative AI Project  
Division D9 – Group07D9
