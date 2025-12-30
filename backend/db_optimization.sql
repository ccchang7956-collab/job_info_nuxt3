-- 資料庫索引優化建議
-- 執行以下 SQL 以提升查詢效能

-- 1. 複合索引：用於 history_count 子查詢
-- 加速同機關同職務的歷史職缺查詢
CREATE INDEX IF NOT EXISTS idx_job_history_lookup 
ON job_all_data (org_name, work_item, date_from);

-- 2. 留言計數索引：加速留言數查詢
CREATE INDEX IF NOT EXISTS idx_comments_job_id_deleted 
ON job_comments (job_all_data_id, is_deleted);

-- 3. 檢查現有索引是否有效運作
SHOW INDEX FROM job_all_data;
SHOW INDEX FROM job_comments;

-- 4. 分析表格以更新統計資訊
ANALYZE TABLE job_all_data;
ANALYZE TABLE job_comments;
