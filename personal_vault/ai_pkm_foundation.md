# AI PKM Foundation System

## Overview
This is my personal knowledge management (PKM) system built with AI-powered search and retrieval capabilities. The system uses vector embeddings to enable semantic search across all my notes and documentation.

## Architecture

### Components
1. **Ingestion Pipeline**
   - Watches markdown files in personal_vault directory
   - Chunks content into manageable pieces (500 tokens)
   - Generates embeddings using sentence-transformers
   - Stores in Supabase with pgvector

2. **Search System**
   - Semantic similarity search using cosine distance
   - Returns most relevant content chunks
   - Supports filtering by source/metadata

3. **MCP Integration**
   - Model Context Protocol server for tool integration
   - Enables AI assistants to search and retrieve knowledge
   - Web crawling capabilities for external content

## Key Technologies
- **Vector Database**: Supabase with pgvector extension
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Search**: Cosine similarity search
- **Storage**: Markdown files with automatic sync

## Benefits
- Fast semantic search across all knowledge
- AI-powered retrieval and summarization
- Automatic ingestion of new content
- Integration with AI assistants via MCP

## Future Enhancements
- Multi-modal embeddings (text + images)
- Knowledge graph visualization
- Automatic tagging and categorization
- Cross-reference detection