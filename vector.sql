CREATE TABLE users_c54a1e31 (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(200),
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sources_c54a1e31 (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    base_url VARCHAR(500) UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE articles_c54a1e31 (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources_c54a1e31(id),
    url VARCHAR(1000) UNIQUE NOT NULL,
    title VARCHAR(1000) NOT NULL,
    authors VARCHAR(500),
    publication_date TIMESTAMP,
    fetched_at TIMESTAMP,
    http_status INTEGER,
    word_count INTEGER,
    content TEXT,
    summary TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE article_extractions_c54a1e31 (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles_c54a1e31(id) NOT NULL,
    extraction_type VARCHAR(100) NOT NULL,
    extraction_text TEXT NOT NULL,
    confidence DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_saved_articles_c54a1e31 (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_c54a1e31(id) NOT NULL,
    article_id INTEGER REFERENCES articles_c54a1e31(id) NOT NULL,
    note TEXT,
    is_selected BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chats_c54a1e31 (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_c54a1e31(id) NOT NULL,
    title VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_article_links_c54a1e31 (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER REFERENCES chats_c54a1e31(id) NOT NULL,
    article_id INTEGER REFERENCES articles_c54a1e31(id) NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_messages_c54a1e31 (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER REFERENCES chats_c54a1e31(id) NOT NULL,
    user_id INTEGER REFERENCES users_c54a1e31(id),
    role VARCHAR(50) NOT NULL, -- e.g., 'user', 'assistant', 'system'
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_c54a1e31_email ON users_c54a1e31(email);
CREATE INDEX idx_users_c54a1e31_username ON users_c54a1e31(username);
CREATE INDEX idx_sources_c54a1e31_name ON sources_c54a1e31(name);
CREATE INDEX idx_articles_c54a1e31_url ON articles_c54a1e31(url);
CREATE INDEX idx_articles_c54a1e31_title ON articles_c54a1e31(title);
CREATE INDEX idx_articles_c54a1e31_publication_date ON articles_c54a1e31(publication_date);
CREATE INDEX idx_articles_c54a1e31_source_id ON articles_c54a1e31(source_id);
CREATE INDEX idx_article_extractions_c54a1e31_article_id ON article_extractions_c54a1e31(article_id);
CREATE INDEX idx_user_saved_articles_c54a1e31_user_id ON user_saved_articles_c54a1e31(user_id);
CREATE INDEX idx_chats_c54a1e31_user_id ON chats_c54a1e31(user_id);
CREATE INDEX idx_chat_messages_c54a1e31_chat_id ON chat_messages_c54a1e31(chat_id);
CREATE INDEX idx_chat_messages_c54a1e31_created_at ON chat_messages_c54a1e31(created_at);
CREATE INDEX idx_chat_article_links_c54a1e31_chat_id ON chat_article_links_c54a1e31(chat_id);

INSERT INTO users_c54a1e31 (username, email, display_name, is_admin) VALUES
    ('admin', 'admin@example.com', 'Site Admin', TRUE),
    ('jane_doe', 'jane.doe@example.com', 'Jane Doe', FALSE),
    ('mark_reader', 'mark@example.com', 'Mark Reader', FALSE);

INSERT INTO sources_c54a1e31 (name, base_url, description) VALUES
    ('Global News Daily', 'https://www.globalnews.example', 'International news outlet covering world events.'),
    ('Tech Insider', 'https://techinsider.example', 'Technology news and analysis.'),
    ('Local Post', 'https://localpost.example', 'Community and local city reporting.');

INSERT INTO articles_c54a1e31 (source_id, url, title, authors, publication_date, fetched_at, http_status, word_count, content, summary, tags) VALUES
    (1, 'https://www.globalnews.example/world/2025/08/19/peace-talks', 'Breakthrough in Peace Talks Between Nations', 'Alice Martin', '2025-08-18 09:30:00', '2025-08-18 09:35:22', 200, 820, 'Full article content text goes here. It contains paragraphs of details about the negotiations, statements from officials, and background context.', 'High-level summary: Diplomatic talks led to preliminary agreement on trade and security matters.', 'diplomacy,world,trade'),
    (2, 'https://techinsider.example/articles/ai-privacy-2025', 'New Guidelines for AI and User Privacy', 'Ravi Singh', '2025-08-17 14:00:00', '2025-08-17 14:02:10', 200, 1150, 'Article content discussing new guidelines proposed for AI systems, privacy controls, and regulatory impacts.', 'Summary: Industry groups and regulators propose updated privacy guidance for AI products.', 'ai,privacy,policy'),
    (3, 'https://localpost.example/city/parks-renovation', 'City Approves Major Parks Renovation Plan', 'Maria Lopez', '2025-08-16 08:15:00', '2025-08-16 08:20:00', 200, 540, 'Local article describing approved budget, timelines, and community input for park renovations across the city.', 'Summary: Council approved a multi-year renovation plan for several parks.', 'local,community,parks');

INSERT INTO article_extractions_c54a1e31 (article_id, extraction_type, extraction_text, confidence) VALUES
    (1, 'summary', 'Diplomatic talks resulted in a framework agreement addressing trade quotas and security cooperation.', 0.9400),
    (1, 'entities', 'Alice Martin; Foreign Minister; Trade Commission', 0.8500),
    (2, 'summary', 'Proposed guidelines focus on data minimization, user consent, and auditability for AI systems.', 0.9100),
    (2, 'keywords', 'AI, privacy, regulation, audit', 0.7800),
    (3, 'summary', 'City council approved funds and a timeline to renovate neighborhood parks over the next three years.', 0.8700);

INSERT INTO user_saved_articles_c54a1e31 (user_id, article_id, note, is_selected) VALUES
    (2, 1, 'Relevant for international relations briefing', TRUE),
    (2, 2, 'Follow-up for privacy policy research', TRUE),
    (3, 3, 'Share with local community group', TRUE);

INSERT INTO chats_c54a1e31 (user_id, title, is_active) VALUES
    (2, 'Discussion on AI privacy guidelines', TRUE),
    (2, 'World affairs: peace talks follow-up', TRUE),
    (3, 'Community parks project planning', TRUE);

INSERT INTO chat_article_links_c54a1e31 (chat_id, article_id, note) VALUES
    (1, 2, 'Primary article for policy discussion'),
    (2, 1, 'Source article for follow-up questions'),
    (3, 3, 'Reference for community meeting agenda');

INSERT INTO chat_messages_c54a1e31 (chat_id, user_id, role, message) VALUES
    (1, 2, 'user', 'I want to discuss how the new guidelines will affect small startups.'),
    (1, 1, 'assistant', 'We can review the summary and extract key compliance items relevant to startups.'),
    (2, 2, 'user', 'Can you summarize the security provisions from the peace talks article?'),
    (2, 1, 'assistant', 'Summary: The agreement mentions joint patrols and shared intelligence frameworks.'),
    (3, 3, 'user', 'What are the timelines mentioned for the main park renovations?'),
    (3, 1, 'assistant', 'The article states a multi-year plan starting Q1 next year with phased work over three years.');