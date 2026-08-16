------------------------------------------------------------------------------------------------------------------------ 1
-- WITH user_activity AS ( -- take all activities of the user and their dates
--     SELECT A.user_id, A.registration_date , B.completed_at
--     FROM users A INNER JOIN user_lessons B
--     ON A.user_id = B.user_id
--     UNION ALL
--     SELECT A.user_id , A.registration_date, B.finished_at
--     FROM users A INNER JOIN test_attempts B
--     ON A.user_id = B.user_id),
--
-- user_stat AS ( -- flag whether the user is active on the n-th day
--     SELECT DISTINCT ON (user_id) *, CASE WHEN latest_activity >= 1 THEN 1 ELSE 0 END day1 , CASE WHEN latest_activity > 6 THEN 1 ELSE 0 END day7, CASE WHEN latest_activity > 29 THEN 1 ELSE 0 END day30
--     FROM ( -- look for the latest activity
--         SELECT *, LAST_VALUE(completed_at) over (PARTITION BY user_id ORDER BY completed_at rows between unbounded preceding and UNBOUNDED FOLLOWING)::date - registration_date AS latest_activity
--         FROM user_activity
--         WHERE registration_date BETWEEN '2026-02-01' AND '2026-03-01')Q -- metric for february
--     ORDER BY user_id, latest_activity DESC)
--
-- SELECT CAST(SUM(day1) AS DECIMAL)/COUNT(*) AS retention_rate_1day, CAST(SUM(day7) AS DECIMAL)/COUNT(*) AS retention_rate_7day, CAST(SUM(day30) AS DECIMAL)/COUNT(*) AS retention_rate_30day -- the ratio
-- FROM user_stat;
--
-- SELECT * FROM ( -- proof that nobody renews the subscription
--     SELECT A.user_id, COUNT(A.user_id) as cnt
--     FROM users A INNER JOIN subscriptions B
--     ON A.user_id = B.user_id
--     GROUP BY A.user_id
--               )Q where cnt > 1;
--
---- the same calculation for january
-- WITH user_activity AS (
--     SELECT A.user_id, A.registration_date , B.completed_at
--     FROM users A INNER JOIN user_lessons B
--     ON A.user_id = B.user_id
--     UNION ALL
--     SELECT A.user_id , A.registration_date, B.finished_at
--     FROM users A INNER JOIN test_attempts B
--     ON A.user_id = B.user_id),
--
-- user_stat AS (
--     SELECT DISTINCT ON (user_id) *, CASE WHEN latest_activity >= 1 THEN 1 ELSE 0 END day1 , CASE WHEN latest_activity > 6 THEN 1 ELSE 0 END day7, CASE WHEN latest_activity > 29 THEN 1 ELSE 0 END day30
--     FROM (
--         SELECT *, LAST_VALUE(completed_at) over (PARTITION BY user_id ORDER BY completed_at rows between unbounded preceding and UNBOUNDED FOLLOWING)::date - registration_date AS latest_activity
--         FROM user_activity
--         WHERE registration_date BETWEEN '2026-01-01' AND '2026-02-01')Q
--     ORDER BY user_id, latest_activity DESC)
--
-- SELECT CAST(SUM(day1) AS DECIMAL)/COUNT(*) AS retention_rate_1day, CAST(SUM(day7) AS DECIMAL)/COUNT(*) AS retention_rate_7day, CAST(SUM(day30) AS DECIMAL)/COUNT(*) AS retention_rate_30day
-- FROM user_stat;

-- ------------------------------------------------------------------------------------------------------------------------2
--
-- WITH merged_table as (
--     SELECT b.lesson_id, B.user_id, B.score, C.subject_id
--     FROM user_lessons B INNER JOIN lessons C
--     ON B.lesson_id = C.lesson_id),
--
-- -- SELECT lesson_id, COUNT(lesson_id) -- check how many times a lesson was taken, so we do not read unpopular ones as hard ones
-- -- FROM merged_table
-- -- GROUP BY lesson_id
--
-- -- SELECT COUNT(*), COUNT(DISTINCT (user_id, lesson_id)) -- make sure every student takes a lesson only once
-- -- FROM  merged_table
--
-- lesson_rate as (
--     SELECT subject_id, lesson_id, AVG(score) as score
--     FROM merged_table
--     GROUP BY subject_id, lesson_id),
--
-- lesson_rank as (
--     SELECT *, ROW_NUMBER() over (PARTITION BY subject_id ORDER BY score ASC) AS rnk
--     FROM lesson_rate
--     )
--
-- SELECT *
-- FROM lesson_rank
-- WHERE rnk <= 3
-- ORDER BY subject_id, rnk;

-- ------------------------------------------------------------------------------------------------------------------------3
--
SELECT * -- one student - one successful attempt
FROM (
    SELECT user_id, COUNT(user_id) AS cnt
    FROM test_attempts A INNER JOIN tests B
    ON A.test_id = B.test_id
    WHERE score > 140
    GROUP BY user_id)q
WHERE cnt > 1;

SELECT AVG(finished_at - started_at)
FROM test_attempts A INNER JOIN tests B
ON A.test_id = B.test_id
WHERE score > 140;

SELECT MAX(finished_at - started_at) -- confirm the assumption that the max is 2 hours
FROM test_attempts A INNER JOIN tests B
ON A.test_id = B.test_id
WHERE score > 140;

SELECT MIN(finished_at - started_at) -- looking for anomalies
FROM test_attempts A INNER JOIN tests B
ON A.test_id = B.test_id
WHERE score > 140
