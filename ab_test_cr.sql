-- conversion into a subscription for variant A
SELECT COUNT(a.user_id)*1.0/COUNT(*)
FROM subscriptions A INNER JOIN subscription_plans B
ON A.plan_id = B.plan_id
RIGHT JOIN ab_test_segments AS C
ON A.user_id = C.user_id
INNER JOIN users D
ON C.user_id = D.user_id
WHERE variant = 'A';

-- conversion into a subscription for variant B
SELECT COUNT(a.user_id)*1.0/COUNT(*)
FROM subscriptions A INNER JOIN subscription_plans B
ON A.plan_id = B.plan_id
RIGHT JOIN ab_test_segments AS C
ON A.user_id = C.user_id
INNER JOIN users D
ON C.user_id = D.user_id
WHERE variant = 'B';

-- raw data for a check
SELECT *
FROM subscriptions

