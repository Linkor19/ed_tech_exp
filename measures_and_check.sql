-- SELECT * FROM subscriptions LIMIT 10;
-- SELECT * FROM subscription_plans LIMIT 10;

-- SELECT max(end_date)
-- FROM subscriptions
-- WHERE status = 'Expired';

-- SELECT min(end_date)
-- FROM subscriptions
-- WHERE status = 'Active';

-- SELECT  *
-- FROM subscriptions
-- WHERE end_date BETWEEN '2026-03-28'::date AND '2026-03-31'::date;

-- SELECT *
-- FROM subscriptions
-- WHERE end_date < '2026-03-31'::date AND status = 'Expired';

-- all subscriptions active after 03-31 are valid
-- all subscriptions not active after 03-28 are expired


DROP VIEW user_sub;
CREATE VIEW user_sub AS ( -- a general view built around the subscriptions
    SELECT a.user_id, registration_date, platform, marketing_chanel,
           subscription_id, b.plan_id, standart_price, start_date, end_date, price_paid,
           plan_name, duration_days as acquistion_cost
    --EXTRACT(DAY FROM end_date - start_date)
    FROM users A LEFT JOIN subscriptions B
    ON A.user_id = B.user_id
    LEFT JOIN  subscription_plans C
    ON B.plan_id = C.plan_id
--     LEFT JOIN marketing_costs D
--     ON A.marketing_chanel = D.channel AND a.registration_date::date = d.date
         -- AND d.date = (SELECT MIN(date) FROM marketing_costs WHERE a.registration_date::date <= date); -- in case there were gaps in the rates between the days
--     WHERE price_paid < standart_price
    -- WHERE duration_days = EXTRACT(DAY FROM end_date - start_date)
);

SELECT *
FROM user_sub;


--the paid price can be lower than the standard one, but never higher than the standard one!

-- --channels
-- SELECT DISTINCT (users.marketing_chanel)
-- FROM users;
--
-- --number of users
-- SELECT marketing_chanel, COUNT(users.user_id)
-- FROM users
-- GROUP BY marketing_chanel;
--
---- arpu and arppu
-- SELECT marketing_chanel, sum(price_paid) / COUNT (user_id), sum(price_paid) / COUNT(plan_id)
-- FROM user_sub
-- GROUP BY marketing_chanel;

-- -- -- total revenue by channel
-- SELECT marketing_chanel,  SUM(price_paid)
-- FROM user_sub
-- GROUP BY marketing_chanel ;

-- -- rates without gaps
-- SELECT date, COUNT(date)
-- FROM marketing_costs
-- GROUP BY date
-- HAVING COUNT(date) <> 3

---- total spent on the campaign
-- SELECT channel, SUM(cost)
-- FROM marketing_costs
-- GROUP BY channel
--
-- -- -- cost of acquiring a user
-- SELECT marketing_chanel, spend/users_acquisition
-- FROM(
--     SELECT marketing_chanel, COUNT(user_id) as users_acquisition
--     FROM user_sub
--     GROUP BY marketing_chanel)Q INNER JOIN
--     (SELECT channel, SUM(cost) as spend
--      FROM marketing_costs
--      GROUP BY channel )B
-- ON Q.marketing_chanel = B.channel

--
-- -- cost of acquiring a premium user
-- SELECT marketing_chanel, spend/users_acquisition
-- FROM(
--     SELECT marketing_chanel, COUNT(user_id) FILTER ( WHERE subscription_id IS NOT NULL ) users_acquisition
--     FROM user_sub
--     GROUP BY marketing_chanel)Q INNER JOIN
--     (SELECT channel, SUM(cost) as spend
--      FROM marketing_costs
--      GROUP BY channel )B
-- ON Q.marketing_chanel = B.channel


---- romi
-- SELECT marketing_chanel, (earnd - spend) / spend as romi
-- FROM
--     (SELECT marketing_chanel, SUM(price_paid) as earnd
--     FROM user_sub
--     GROUP BY marketing_chanel) Q
--     INNER JOIN
--     (   SELECT channel, SUM(cost) as spend
--         FROM marketing_costs
--         GROUP BY channel) B
-- ON Q.marketing_chanel = B.channel;

SELECT *
FROM user_sub

--

------------------------------------------------------------------------------------------------------------------------
-- SELECT *
-- FROM clickstream_logs
-- WHERE event_timestamp::date = '2026-02-15'
-- ORDER BY session_id, event_timestamp ASC;

-- -- check for a repeated timestamp
-- SELECT *
-- FROM (
--     SELECT *,COUNT (event_timestamp) OVER (PARTITION BY user_id, event_timestamp) as uniqe_event
--     FROM clickstream_logs
--     )Q
-- WHERE uniqe_event > 1
-- ORDER BY user_id, event_timestamp

-- -- check for a full duplicate
-- SELECT *
-- FROM (
--     SELECT *,COUNT (event_timestamp) OVER (PARTITION BY user_id, event_timestamp, screen_name) as uniqe_event
--     FROM clickstream_logs
--     )Q
-- WHERE uniqe_event > 1
-- ORDER BY user_id, event_timestamp

-- -- Check for duplicated logs (the number of sessions is bigger than the number of users)
-- SELECT event_timestamp::date, COUNT(DISTINCT(session_id)) as sessions, COUNT(DISTINCT (user_id)) as users
-- FROM clickstream_logs
-- GROUP BY event_timestamp::date
-- -- HAVING COUNT(DISTINCT(session_id)) <>COUNT(DISTINCT (user_id))
--
-- WITH error_logs AS( -- REPEATED LOGS
--     SELECT *
--     FROM(
--         SELECT *, screen_name as actual_event, LEAD(screen_name) OVER (PARTITION BY user_id ORDER BY session_id, event_id) as next_event
--         FROM clickstream_logs)Q
--     WHERE actual_event = next_event)
--
-- -- DELETE FROM error_logs -- deleting the duplicates
-- -- WHERE event_id IN (
-- --     SELECT event_id
-- --     FROM error_logs
-- --     )
--
-- SELECT COUNT(DISTINCT (session_id)) -- number of duplicates
-- FROM error_logs;

--
--    -- dau calculation
-- SELECT AVG(users)
-- FROM (
--     SELECT event_timestamp::date, COUNT(DISTINCT(session_id)) as sessions, COUNT(DISTINCT (user_id)) as users
--     FROM clickstream_logs
--     GROUP BY event_timestamp::date)Q

-- -- total count of the funnel parts
-- SELECT screen_name, COUNT(screen_name)
-- FROM clickstream_logs
-- GROUP BY screen_name;
--
--
-- SELECT *
-- FROM (
--     SELECT user_id, session_id, event_id, screen_name as first_step, LEAD(screen_name, 1) OVER (PARTITION BY session_id ORDER BY event_id) as second_step,
--            LEAD(screen_name, 2) OVER (PARTITION BY session_id ORDER BY event_id) as third_step,
--            LEAD(screen_name, 3) OVER (PARTITION BY session_id ORDER BY event_id) as fourth_step,
--            LEAD(screen_name, 4) OVER (PARTITION BY session_id ORDER BY event_id) as fifth_step
--     FROM clickstream_logs)Q
-- WHERE event_id = (SELECT MIN(event_id) FROM clickstream_logs WHERE Q.session_id = clickstream_logs.session_id) AND
--       (first_step <> 'Onboarding_1' OR second_step <> 'Onboarding_2' OR third_step <> 'Main_Dashboard' OR fourth_step <> 'Lesson_List' OR fifth_step <> 'Paywall');



