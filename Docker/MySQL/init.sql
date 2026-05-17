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
        study_time TIME NOT NULL,
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
        deleted_at DATETIME (6) DEFAULT NULL,
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
        PRIMARY KEY (id),
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- チェーン管理テーブル
CREATE TABLE chain (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
)ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE 
    Baton (
        id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,           -- バトンID
        baton_title VARCHAR(25) NOT NULL,                              -- バトンタイトル
        sender_id   BIGINT UNSIGNED NOT NULL,                          -- 送信者ID
        receiver_id BIGINT UNSIGNED NOT NULL,                          -- 受信者ID
        task_id     BIGINT UNSIGNED NOT NULL,                          -- 課題ID
        content     TEXT NOT NULL,                                     -- バトン内容
        chain_id    BIGINT UNSIGNED NOT NULL,                          -- チェインID
        relay_count BIGINT UNSIGNED NOT NULL,                          -- 今何人目か
        status      TINYINT NOT NULL DEFAULT 0,                        -- ステータス(0:未完了 1:完了 2:失敗)
        batonpop    TINYINT NOT NULL DEFAULT 0,                        -- 通知フラグ(0:未通知 1:通知済み)
        get_at      DATETIME(6) DEFAULT NULL,                          -- 受け取り日時
        release_at  DATETIME(6) DEFAULT NULL,                          -- 渡し日時
        created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), -- 作成日時
        updated_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6), -- 更新日時
        PRIMARY KEY (id),
        KEY idx_baton_sender_id   (sender_id),
        KEY idx_baton_receiver_id (receiver_id),
        KEY idx_baton_task_id     (task_id),
        KEY idx_baton_chain_id    (chain_id),
        KEY idx_baton_created_at  (created_at),
        CONSTRAINT fk_baton_sender   FOREIGN KEY (sender_id)   REFERENCES users (id),
        CONSTRAINT fk_baton_receiver FOREIGN KEY (receiver_id) REFERENCES users (id),
        CONSTRAINT fk_baton_task     FOREIGN KEY (task_id)     REFERENCES tasks (id),
        CONSTRAINT fk_chain_id       FOREIGN KEY (chain_id)    REFERENCES chain (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- バトン予約テーブル
CREATE TABLE baton_queues (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    baton_title VARCHAR(25) NOT NULL,
    sender_id BIGINT UNSIGNED NOT NULL,
    chain_id BIGINT UNSIGNED NOT NULL,
    relay_count BIGINT UNSIGNED NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    KEY idx_baton_queues_sender_id   (sender_id),
    KEY idx_baton_queues_chain_id   (chain_id),
    KEY idx_baton_queues_created_at   (created_at)
)ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

/* バトンID(旧式)
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

*/
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

/* 勉強ID
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

*/

/*リアクションユーザーID(いらないかも)
CREATE TABLE
    Re_users (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        content TEXT NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
*/

-- リアクションID
CREATE TABLE
    post_reactions (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,     -- リアクションID 主キー
        post_id BIGINT UNSIGNED NOT NULL,               -- 投稿id参照　外部キー
        user_id BIGINT UNSIGNED NOT NULL,               -- ユーザーid参照　外部キー
        emoji_type VARCHAR(50) NOT NULL,                -- スタンプ内容
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- リアクション日時
        PRIMARY KEY (id),
        UNIQUE KEY unique_user_reaction(post_id,user_id,emoji_type), -- 同じ人が同じリアクションをしないようにする制約
        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        -- ON DELETE CASCADE 連動削除機能。投稿が消えると紐づいているリアクションも一緒に消える
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;


INSERT INTO users (name, email, password)
VALUES 
  ('Tomo', 'Tomo64@example.com', '0c120c7ab57b43d4db1837f2a4332ced20b2f3160bdeb186a8d601e3b0d6ace5'),
  ('おっくん', 'okun@example.com', '165d68fe9913a11c91bb7290d5d885833240c0fdb43b0b2be790f043bc9022c7'),
  ('てる', 'teru@example.com', '44b4c21936c779156df19a17832a0d91ecbfb37e6889ef6d9b465c75b00ef060'),
  ('たまちゃん', 'tamachan@example.com', 'ee839106f2f14fab267dd94f311a152490e256e69e612e4d73b710c5fc9b7ef7'),
  ('まつけん', 'matuken@example.com', '2935bf31052e67f5ff0ba4f37e9f6ef3964831dfeee316fee07cef4ab9803a62');


INSERT INTO posts (user_id, content,study_time)
VALUES
  (1, 'こんにちは！数学勉強中です！','01:30:00'),
  (2, '試験頑張ってきます','05:30:00'),
  (3, 'ハッカソンの会議の日です！', '00:45:00');


INSERT INTO comments (user_id, post_id, content)
VALUES
    (2, 1, '私もがんばります！'),
    (3, 2, '応援しています！頑張ってください。'),
    (1, 3, '22時からですね！');

INSERT INTO tasks(content)
VALUES
('今日授業で習ったこと、1つ教えて！') ,
('最近のマナビで「へーー」って思ったこと教えてー ') ,
('得意な教科の問題、何でもいいから3問解いてみて！ ') ,
('苦手な教科の教科書を1ページだけ音読しろ ') ,
('「これ知らんやろ」って思ってること教えて') ,
('昨日より1ミリだけ賢くなったこと教えて') ,
('ノートのどっか1行だけ写してみて') ,
('今日の授業で一番どうでもよかったこと教えて') ,
('3分だけ何か勉強して「やった」って言い切れ') ,
('英単語1個だけ覚えてドヤって') ,
('「これテスト出そう」って勝手に予想してみて') ,
('今日の先生の話で一番印象に残ったフレーズ教えて') ,
('数学でも英語でもいいから“1問だけ”倒してこい') ,
('ノート開いた瞬間スクショ（証拠）') ,
('「なんとなく理解した気がする」ことを説明してみて') ,
('30秒だけ教科書読んで、覚えてる単語3つ書け') ,
('友達に1つだけ勉強の話ふってみて（内容も書け）') ,
('今日の授業を一言でまとめろ（雑でOK）') ,
('「これ誰かに教えたい」って思うこと1つ書いて') ,
('過去の自分に1行だけアドバイスするとしたら？') ,
('「これ一生使わんやろ」って思った知識教えて') ,
('勉強に関係ありそうでなさそうな豆知識1つ') ,
('今日の集中力を10点満点で評価して理由もどうぞ') ,
('1分だけタイマーなしで集中してみて感想書け') ,
('今の気分で一番マシな教科に1秒触れろ（開くだけOK）') ;


INSERT INTO chain(id) VALUES(1);

INSERT INTO Baton (baton_title,sender_id, receiver_id, task_id,content,chain_id,relay_count,status)
VALUES
    ('レジェンドバトン！', 2, 1, 1, '今日授業で習ったこと、1つ教えて！', 1, 1, 0);

INSERT INTO post_reactions (post_id, user_id, emoji_type) 
VALUES
(1, 2, X'F09F918D'),    -- [グーサイン] (16進数)
(2, 3, X'E29DA4'),      -- [ハート] (16進数)
(3, 1, X'F09F9882'),    -- [泣き笑い] (16進数)
(1, 3, X'F09F98AD') ;   -- [号泣] (16進数)