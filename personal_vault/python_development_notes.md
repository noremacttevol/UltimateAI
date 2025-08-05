# Python Development Notes

## Best Practices

### Code Organization
- Use virtual environments for every project
- Follow PEP 8 style guidelines
- Implement proper error handling with try/except blocks
- Use type hints for better code documentation

### Testing
- Write unit tests using pytest
- Aim for high test coverage (>90%)
- Use fixtures for reusable test data
- Mock external dependencies

### Documentation
- Use docstrings for all functions and classes
- Keep README files up to date
- Document API endpoints with examples
- Use meaningful variable and function names

## AI/ML Development

### Embeddings
- sentence-transformers for text embeddings
- OpenAI embeddings for production use
- Consider dimensionality vs performance tradeoffs
- Normalize embeddings for cosine similarity

### Vector Databases
- Supabase with pgvector for PostgreSQL
- Pinecone for managed vector search
- FAISS for local/experimental work
- Chroma for development and prototyping

### RAG Systems
- Chunk text appropriately (300-1000 tokens)
- Use overlap for better context preservation
- Implement hybrid search (vector + keyword)
- Cache embeddings to reduce API costs

## Tools and Libraries

### Essential Packages
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `requests` - HTTP client
- `python-dotenv` - Environment variables
- `sqlalchemy` - Database ORM
- `fastapi` - API development
- `streamlit` - Quick UI prototypes

### Development Tools
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking
- `pytest` - Testing framework
- `poetry` - Dependency management