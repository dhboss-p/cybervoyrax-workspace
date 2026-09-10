CREATE TABLE IF NOT EXISTS notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(160) NOT NULL,
    body VARCHAR(500) NOT NULL,
    link_url VARCHAR(255) NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    CONSTRAINT fk_notifications_user
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS workspace_settings (
    id TINYINT PRIMARY KEY,
    workspace_name VARCHAR(120) NOT NULL,
    default_document_visibility ENUM('PRIVATE','PROJECT_MEMBERS','MANAGERS','COMPANY')
      NOT NULL DEFAULT 'PROJECT_MEMBERS',
    session_duration_minutes INT NOT NULL DEFAULT 480,
    remember_me_days INT NOT NULL DEFAULT 14,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO workspace_settings (
    id, workspace_name, default_document_visibility,
    session_duration_minutes, remember_me_days
)
VALUES (1, 'CYBERVOYRAX Workspace', 'PROJECT_MEMBERS', 480, 14)
ON DUPLICATE KEY UPDATE workspace_name = VALUES(workspace_name);

CREATE INDEX idx_notifications_user_read
ON notifications (user_id, is_read, created_at);

CREATE INDEX idx_projects_manager
ON projects (manager_user_id);

CREATE INDEX idx_project_members_user
ON project_members (user_id);

CREATE INDEX idx_documents_owner
ON documents (owner_user_id);
