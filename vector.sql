CREATE TABLE sessions_84f04d32 (
    id SERIAL PRIMARY KEY,
    session_uuid VARCHAR(36) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scrape_requests_84f04d32 (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions_84f04d32(id),
    urls TEXT NOT NULL,
    prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE articles_84f04d32 (
    id SERIAL PRIMARY KEY,
    scrape_id INTEGER REFERENCES scrape_requests_84f04d32(id),
    session_id INTEGER REFERENCES sessions_84f04d32(id),
    title VARCHAR(500) NOT NULL,
    author VARCHAR(255),
    published_at TIMESTAMP,
    summary TEXT,
    body TEXT,
    tags TEXT,
    url VARCHAR(2048),
    filename VARCHAR(255),
    ingested BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE files_84f04d32 (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles_84f04d32(id),
    filename VARCHAR(255) NOT NULL,
    file_base64 TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chunks_84f04d32 (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES files_84f04d32(id),
    chunk_index INTEGER NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_messages_84f04d32 (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions_84f04d32(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_responses_84f04d32 (
    id SERIAL PRIMARY KEY,
    chat_message_id INTEGER REFERENCES chat_messages_84f04d32(id),
    response TEXT,
    context_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_response_chunks_84f04d32 (
    id SERIAL PRIMARY KEY,
    chat_response_id INTEGER REFERENCES chat_responses_84f04d32(id),
    filename VARCHAR(255),
    chunk_id INTEGER,
    content TEXT,
    distance DECIMAL(8,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_84f04d32_uuid ON sessions_84f04d32(session_uuid);
CREATE INDEX idx_scrape_84f04d32_session ON scrape_requests_84f04d32(session_id);
CREATE INDEX idx_articles_84f04d32_title ON articles_84f04d32(title);
CREATE INDEX idx_articles_84f04d32_url ON articles_84f04d32(url);
CREATE INDEX idx_files_84f04d32_filename ON files_84f04d32(filename);
CREATE INDEX idx_chunks_84f04d32_file ON chunks_84f04d32(file_id);
CREATE INDEX idx_chat_messages_84f04d32_session ON chat_messages_84f04d32(session_id);
CREATE INDEX idx_chat_responses_84f04d32_chatmsg ON chat_responses_84f04d32(chat_message_id);
CREATE INDEX idx_chat_resp_chunks_84f04d32_response ON chat_response_chunks_84f04d32(chat_response_id);

INSERT INTO sessions_84f04d32 (session_uuid, name) VALUES
    ('c0b9f9a8-9a9a-4e9a-8a5f-4a2f2b5e0001', 'News Session'),
    ('a1b2c3d4-1111-2222-3333-444455556666', 'Research Session');

INSERT INTO scrape_requests_84f04d32 (session_id, urls, prompt) VALUES
    (1, 'https://news.site/article1\nhttps://news.site/article2', 'Extract title author date summary body tags'),
    (2, 'https://example.com/news1', 'Extract title author date summary body tags');

INSERT INTO articles_84f04d32 (scrape_id, session_id, title, author, published_at, summary, body, tags, url, filename, ingested) VALUES
    (1, 1, 'Sample Title One', 'John Doe', '2025-01-01 10:00:00', 'Short summary one', 'Full body text one', 'news,tech', 'https://news.site/article1', 'article-1.txt', false),
    (1, 1, 'Sample Title Two', 'Jane Smith', '2025-01-02 11:00:00', 'Short summary two', 'Full body text two', 'news,world', 'https://news.site/article2', 'article-2.txt', false),
    (2, 2, 'Test Article', 'John Doe', '2025-02-01 09:00:00', 'Short summary', 'Full body text', 'sample', 'https://example.com/news1', 'news1.txt', false);

INSERT INTO files_84f04d32 (article_id, filename, file_base64) VALUES
    (1, 'article-1.txt', 'base64data'),
    (2, 'article-2.txt', 'base64data'),
    (3, 'news1.txt', 'base64data');

INSERT INTO chunks_84f04d32 (file_id, chunk_index, content) VALUES
    (1, 1, 'Simple chunk text one'),
    (1, 2, 'Simple chunk text two'),
    (2, 1, 'Simple chunk text three');

INSERT INTO chat_messages_84f04d32 (session_id, role, content) VALUES
    (1, 'user', 'Summarize the main points'),
    (1, 'user', 'What are the key facts');

INSERT INTO chat_responses_84f04d32 (chat_message_id, response, context_used) VALUES
    (1, 'Here are the key points from the articles', true),
    (2, 'Here are the facts from the source', true);

INSERT INTO chat_response_chunks_84f04d32 (chat_response_id, filename, chunk_id, content, distance) VALUES
    (1, 'article-1.txt', 1, 'Simple chunk text one', 0.0800),
    (1, 'article-2.txt', 1, 'Simple chunk text three', 0.1200),
    (2, 'news1.txt', 1, 'Simple chunk text two', 0.0500);