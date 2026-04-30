DROP DATABASE IF EXISTS snsapp;

DROP USER IF EXISTS 'testuser'@'%';


CREATE USER 'testuser'@'%' IDENTIFIED BY 'testuser';

CREATE DATABASE IF NOT EXISTS snsapp
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;


GRANT ALL PRIVILEGES ON snsapp.* TO 'testuser'@'%';

FLUSH PRIVILEGES;

USE snsapp;

-- アカウントID
CREATE TABLE
    users (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id),
        UNIQUE KEY uq_users_email (email)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- 投稿ID
CREATE TABLE
    posts (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id BIGINT UNSIGNED NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        deleted_at DATETIME (6) DEFAULT NULL,
        PRIMARY KEY (id),
        KEY idx_posts_user_id (user_id),
        CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- コメントID
CREATE TABLE
    comments (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id BIGINT UNSIGNED NOT NULL,
        post_id BIGINT UNSIGNED NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id),
        KEY idx_comments_user_id (user_id),
        KEY idx_comments_post_id (post_id),
        CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_comments_post FOREIGN KEY (post_id) REFERENCES posts (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- 課題ID
CREATE TABLE
    tasks (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        content TEXT NOT NULL,
        menu VARCHAR(255) NOT NULL ,
        PRIMARY KEY (id),
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;


-- バトンID
CREATE TABLE
    Baton (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id BIGINT UNSIGNED NOT NULL,
        task_id BIGINT UNSIGNED NOT NULL,
        content TEXT NOT NULL,
        taskclear_F DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        taskfailed_F DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        batonget_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        get_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        release_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        batonpop BIT(1),
        PRIMARY KEY (id),
        KEY idx_baton_user_id (user_id),
        KEY idx_baton_task_id (task_id),
        CONSTRAINT fk_baton_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_baton_task FOREIGN KEY (task_id) REFERENCES tasks (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;


-- バトン履歴ID
CREATE TABLE
    Batonlogs (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        baton_id BIGINT UNSIGNED NOT NULL,
        content TEXT NOT NULL,
        logs_F BIT(1),
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id),
        KEY idx_batonlogs_user_id (baton_id),
        CONSTRAINT fk_batonlogs_user FOREIGN KEY (baton_id) REFERENCES Baton (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- 勉強ID
CREATE TABLE
    studys (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        post_id BIGINT UNSIGNED NOT NULL,
        content TEXT NOT NULL,
        study_time TIME NOT NULL,
        study_day DATE NOT NULL,
        all_study TIME NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id),
        KEY idx_study_post_id (post_id),
        CONSTRAINT fk_study_post FOREIGN KEY (post_id) REFERENCES posts (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;


-- リアクションユーザーID
CREATE TABLE
    Re_users (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        content TEXT NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- リアクションID
CREATE TABLE
    reactions (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        comment_id BIGINT UNSIGNED NOT NULL,
        Re_user_id BIGINT UNSIGNED NOT NULL,
        content TEXT NOT NULL,
        reaction_F BIT(1),
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id),
        KEY idx_reactions_comment_id (comment_id),
        KEY idx_reactions_Re_user_id (Re_user_id),
        CONSTRAINT fk_reactions_comment_id FOREIGN KEY (comment_id) REFERENCES comments (id),
        CONSTRAINT fk_reactions_Re_user_id FOREIGN KEY (Re_user_id) REFERENCES Re_users (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

INSERT INTO users (name, email, password)
VALUES 
  ('Tomo', 'Tomo64@example.com', '0c120c7ab57b43d4db1837f2a4332ced20b2f3160bdeb186a8d601e3b0d6ace5'),
  ('おっくん', 'okun@example.com', '165d68fe9913a11c91bb7290d5d885833240c0fdb43b0b2be790f043bc9022c7'),
  ('てる', 'qn3dyx11w4ge@example.com', '44b4c21936c779156df19a17832a0d91ecbfb37e6889ef6d9b465c75b00ef060');


INSERT INTO posts (user_id, content)
VALUES
  (1, 'こんにちは！数学勉強中です！'),
  (2, '試験頑張ってきます'),
  (3, 'ハッカソンの会議の日です！');


INSERT INTO comments (user_id, post_id, content)
VALUES
    (2, 1, '私もがんばります！'),
    (3, 2, '応援しています！頑張ってください。'),
    (1, 3, '22時からですね！');