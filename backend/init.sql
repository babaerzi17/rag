-- RBAC 建表语句
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

-- 知识库相关表
DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS chat_sessions;
DROP TABLE IF EXISTS document_chunks;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS knowledge_bases;
DROP TABLE IF EXISTS model_configs;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT  -- 新增description列
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    menu_name VARCHAR(255) NOT NULL,
    description TEXT,
    menu_path VARCHAR(255),
    menu_icon VARCHAR(100),
    parent_id INT,
    sort_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 知识库表
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    color VARCHAR(20),
    is_public BOOLEAN DEFAULT FALSE,
    embedding_model VARCHAR(100),
    vector_store VARCHAR(100) DEFAULT 'chroma',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 文档表
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    knowledge_base_id INT NOT NULL,
    title VARCHAR(255) NOT NULL, -- Changed from filename/original_filename
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    status VARCHAR(20) NOT NULL DEFAULT 'processing',
    page_count INT,
    chunk_count INT DEFAULT 0,
    doc_metadata JSON, -- Renamed from metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 文档块表
CREATE TABLE IF NOT EXISTS document_chunks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    knowledge_base_id INT NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    page_number INT,
    vector_id VARCHAR(255),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    INDEX idx_document_chunk (document_id, chunk_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 聊天会话表
CREATE TABLE IF NOT EXISTS chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT, -- Removed NOT NULL
    knowledge_base_id INT, -- Still nullable in model, but added foreign key ondelete
    title VARCHAR(255),
    model_config JSON, -- Added
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL, -- Added ondelete
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE SET NULL -- Added ondelete
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 聊天消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sources JSON, -- Added
    message_metadata JSON, -- Renamed from metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE -- Added ondelete
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 模型配置表
CREATE TABLE IF NOT EXISTS model_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL, -- Changed length to 50
    model_name VARCHAR(100) NOT NULL, -- Changed length to 100
    api_key VARCHAR(500), -- Changed length to 500
    base_url VARCHAR(255),
    is_default BOOLEAN DEFAULT FALSE,
    config JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(10) NOT NULL,
    module VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    user_id INT,
    user_name VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    details JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 系统备份表
CREATE TABLE IF NOT EXISTS system_backups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,
    backup_type VARCHAR(20) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    error_message TEXT,
    tables_count INT,
    records_count INT,
    files_count INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 系统指标表
CREATE TABLE IF NOT EXISTS system_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    unit VARCHAR(20),
    details JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 性能指标表
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    response_time FLOAT NOT NULL,
    status_code INT NOT NULL,
    user_id INT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    request_size INT,
    response_size INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 模型使用指标表
CREATE TABLE IF NOT EXISTS model_usage_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    total_calls INT NOT NULL DEFAULT 0,
    success_calls INT NOT NULL DEFAULT 0,
    failed_calls INT NOT NULL DEFAULT 0,
    total_tokens INT NOT NULL DEFAULT 0,
    total_cost FLOAT NOT NULL DEFAULT 0.0,
    avg_response_time FLOAT NOT NULL DEFAULT 0.0,
    min_response_time FLOAT,
    max_response_time FLOAT,
    error_details JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) NOT NULL DEFAULT 'string',
    description TEXT,
    is_sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    updated_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 服务健康状态表
CREATE TABLE IF NOT EXISTS service_health (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    response_time FLOAT,
    last_check DATETIME DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    details JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 系统告警表
CREATE TABLE IF NOT EXISTS system_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    metric_value FLOAT,
    threshold_value FLOAT,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at DATETIME,
    resolved_by INT,
    details JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AB测试表
CREATE TABLE IF NOT EXISTS ab_tests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    config JSON,
    group_a_config JSON,
    group_b_config JSON,
    traffic_split FLOAT DEFAULT 0.5,
    sample_size INT,
    duration_days INT,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    started_at DATETIME,
    ended_at DATETIME,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AB测试会话表
CREATE TABLE IF NOT EXISTS ab_test_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_id INT NOT NULL,
    user_id INT NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    group_name VARCHAR(10) NOT NULL, -- Changed from group
    group_config JSON,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    duration_seconds INT,
    total_queries INT DEFAULT 0,
    successful_queries INT DEFAULT 0,
    failed_queries INT DEFAULT 0,
    FOREIGN KEY (test_id) REFERENCES ab_tests(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AB测试交互表
CREATE TABLE IF NOT EXISTS ab_test_interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    query TEXT NOT NULL,
    response TEXT,
    response_time_ms INT,
    retrieved_chunks JSON,
    retrieval_time_ms INT,
    chunk_count INT,
    generation_time_ms INT,
    model_used VARCHAR(100),
    tokens_used INT,
    relevance_score FLOAT,
    accuracy_score FLOAT,
    helpfulness_score FLOAT,
    user_rating INT,
    user_feedback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ab_test_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AB测试指标表
CREATE TABLE IF NOT EXISTS ab_test_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_id INT NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    group_a_value FLOAT,
    group_b_value FLOAT,
    difference FLOAT,
    improvement_percentage FLOAT,
    confidence_level FLOAT,
    p_value FLOAT,
    is_significant BOOLEAN,
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES ab_tests(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 测试问题表
CREATE TABLE IF NOT EXISTS test_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_id INT NOT NULL,
    question TEXT NOT NULL,
    category VARCHAR(100),
    difficulty VARCHAR(20),
    expected_answer TEXT,
    key_points JSON,
    scoring_criteria JSON,
    FOREIGN KEY (test_id) REFERENCES ab_tests(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 问题评估表
CREATE TABLE IF NOT EXISTS question_evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    interaction_id INT NOT NULL,
    evaluator_id INT NOT NULL,
    relevance_score FLOAT,
    accuracy_score FLOAT,
    completeness_score FLOAT,
    clarity_score FLOAT,
    helpfulness_score FLOAT,
    overall_score FLOAT,
    strengths TEXT,
    weaknesses TEXT,
    suggestions TEXT,
    evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES test_questions(id) ON DELETE CASCADE,
    FOREIGN KEY (interaction_id) REFERENCES ab_test_interactions(id) ON DELETE CASCADE,
    FOREIGN KEY (evaluator_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入现有菜单权限（基于项目功能区）
INSERT INTO permissions (name, menu_name, description) VALUES 
('menu:auth', '用户认证', '用户认证相关菜单权限'),       -- 用户认证
('menu:knowledge', '知识库管理', '知识库管理相关菜单权限'),  -- 知识库管理
('menu:document', '文档管理', '文档管理相关菜单权限'),   -- 文档管理
('menu:chat', '智能问答', '智能问答相关菜单权限'),       -- 智能问答
('menu:model', '模型管理', '模型管理相关菜单权限'),      -- 模型管理
('menu:settings', '系统设置', '系统设置相关菜单权限'),   -- 系统设置
('menu:rbac_user', '用户管理', '用户管理菜单权限'),  -- 用户管理
('menu:rbac_role', '角色管理', '角色管理菜单权限'),  -- 角色管理
('menu:rbac_perm', '权限管理', '权限管理菜单权限');  -- 权限管理

-- 创建示例角色
INSERT INTO roles (name, description) VALUES ('admin', '超级管理员'), ('user', '普通用户'), ('guest', '访客');

-- 分配所有菜单权限给admin角色
INSERT INTO role_permissions (role_id, permission_id) 
SELECT r.id, p.id FROM roles r, permissions p WHERE r.name = 'admin' AND p.name LIKE 'menu:%';

-- 分配部分菜单权限给user角色（e.g., chat, knowledge, document, settings）
INSERT INTO role_permissions (role_id, permission_id) 
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'user' AND p.name IN ('menu:chat', 'menu:knowledge', 'menu:document', 'menu:settings');

-- 示例：创建默认admin用户并分配admin角色（密码需哈希，实际用API创建）
-- 这里使用了最新生成的 "Admin.123" 的 bcrypt 哈希值
INSERT INTO users (username, email, hashed_password, full_name, is_active) VALUES ('admin', 'admin@example.com', '$2b$12$2WZa7iZMxJyP.6FjVdCFR.trzEl1C9fTDfR5qgYWxBxgAs68Q1FFS', '系统管理员', TRUE);
INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.username = 'admin' AND r.name = 'admin';

-- 插入示例知识库数据
INSERT INTO knowledge_bases (name, description, type, status, color, is_public, created_by)
SELECT '技术文档库', '包含各种技术文档和API参考', '技术', 'active', '#1976D2', TRUE, u.id
FROM users u WHERE u.username = 'admin';

INSERT INTO knowledge_bases (name, description, type, status, color, is_public, created_by)
SELECT '产品手册', '产品使用说明和常见问题', '产品', 'active', '#388E3C', TRUE, u.id
FROM users u WHERE u.username = 'admin';

INSERT INTO knowledge_bases (name, description, type, status, color, is_public, created_by)
SELECT '培训资料', '内部培训和学习资料', '培训', 'maintenance', '#F57C00', FALSE, u.id
FROM users u WHERE u.username = 'admin';

-- 插入默认模型配置
INSERT INTO model_configs (name, provider, model_name, is_default, config)
VALUES 
('DeepSeek Chat', 'deepseek', 'deepseek-chat', TRUE, '{"temperature": 0.7, "max_tokens": 1000}'),
('OpenAI GPT-3.5', 'openai', 'gpt-3.5-turbo', FALSE, '{"temperature": 0.7, "max_tokens": 1000}');