import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# fix the seed so the results stay reproducible
np.random.seed(42)

start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 3, 31)
days = (end_date - start_date).days

# 1. Reference tables
plans = pd.DataFrame({
    'plan_id': [1, 2, 3],
    'plan_name': ['1 Month Pass', '3 Months Pass', 'Full Season Pass'],
    'duration_days': [30, 90, 180],
    'standard_price': [250, 600, 1000]  # in UAH
})

subjects = pd.DataFrame({
    'subject_id': [1, 2, 3],
    'subject_name': ['Математика', 'Українська мова', 'Історія України']
})

lessons = pd.DataFrame({
    'lesson_id': list(range(1, 16)),
    'subject_id': [1] * 5 + [2] * 5 + [3] * 5,
    'lesson_title': [f'Урок {i}' for i in range(1, 16)],
    'difficulty': np.random.choice(['Easy', 'Medium', 'Hard'], 15)
})

tests = pd.DataFrame({
    'test_id': [101, 102, 103],
    'subject_id': [1, 2, 3],
    'test_type': ['Full Mock', 'Full Mock', 'Full Mock']
})

# 2. Users (generate 5000 users)
num_users = 5000
user_ids = list(range(10001, 10001 + num_users))

reg_dates = [start_date + timedelta(days=int(np.random.exponential(scale=20) % days)) for _ in range(num_users)]
platforms = np.random.choice(['iOS', 'Android'], num_users, p=[0.4, 0.6])
channels = np.random.choice(['Google Search', 'Facebook Ads', 'TikTok Influencers', 'Organic'], num_users,
                            p=[0.3, 0.3, 0.2, 0.2])

users = pd.DataFrame({
    'user_id': user_ids,
    'registration_date': reg_dates,
    'platform': platforms,
    'marketing_channel': channels
})
users['registration_date'] = pd.to_datetime(users['registration_date']).dt.date

# 3. Marketing costs
# IMPORTANT: cost below is the spend of the channel for the WHOLE day, not for one user or one impression
# (I mixed this up once myself and got a cosmic CAC in the analysis - see Ed-tech proj.md)
date_range = pd.date_range(start_date, end_date)
marketing_costs = []
for d in date_range:
    for ch in ['Google Search', 'Facebook Ads', 'TikTok Influencers']:
        base_cost = 400 if ch == 'Facebook Ads' else (300 if ch == 'Google Search' else 250)
        cost = base_cost + np.random.normal(0, 40)
        marketing_costs.append({'date': d.date(), 'channel': ch, 'cost': round(max(50, cost), 2)})
marketing_costs = pd.DataFrame(marketing_costs)

# 4. A/B test (onboarding experiment: ab_onboarding_v2)
# the sneaky trap is simulated right here through the traffic imbalance and Simpson's paradox
ab_test = []
for idx, row in users.iterrows():
    if row['registration_date'] >= datetime(2026, 2, 1).date():
        # artificial skew of the split (Sample Ratio Mismatch + Simpson's paradox)
        if row['platform'] == 'iOS':
            variant = np.random.choice(['A', 'B'], p=[0.8, 0.2])
        else:
            variant = np.random.choice(['A', 'B'], p=[0.2, 0.8])
        ab_test.append({'user_id': row['user_id'], 'experiment_name': 'ab_onboarding_v2', 'variant': variant})
ab_test_segments = pd.DataFrame(ab_test)

# 5. Subscriptions
subscriptions = []
sub_id = 50001
for idx, row in users.iterrows():
    # the base conversion depends on the channel and the platform
    cr = 0.05
    if row['marketing_channel'] == 'Organic': cr = 0.02
    if row['platform'] == 'iOS': cr += 0.05

    # effect of the A/B test (in fact variant B is better on both platforms, but the pooled CR will show a trick - hello, Simpson's paradox)
    is_in_ab = row['user_id'] in ab_test_segments['user_id'].values
    if is_in_ab:
        v = ab_test_segments[ab_test_segments['user_id'] == row['user_id']]['variant'].values[0]
        if row['platform'] == 'iOS':
            cr = 0.10 if v == 'A' else 0.14
        else:
            cr = 0.03 if v == 'A' else 0.05

    if np.random.rand() < cr:
        p_id = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
        plan_info = plans[plans['plan_id'] == p_id].iloc[0]
        days_offset = np.random.randint(0, 10)
        s_date = row['registration_date'] + timedelta(days=days_offset)
        e_date = s_date + timedelta(days=int(plan_info['duration_days']))

        # discounts for retry systems / bug in the promo code logging
        actual_price = plan_info['standard_price']
        if np.random.rand() < 0.15: actual_price *= 0.8

        subscriptions.append({
            'subscription_id': sub_id,
            'user_id': row['user_id'],
            'plan_id': p_id,
            'start_date': s_date,
            'end_date': e_date,
            'status': 'Expired' if e_date < end_date.date() else 'Active',
            'price_paid': round(actual_price, 2)
        })
        sub_id += 1
subscriptions = pd.DataFrame(subscriptions)

# 6. Lessons and test attempts
user_lessons = []
test_attempts = []
attempt_id = 70001

for idx, row in users.iterrows():
    activity_level = np.random.randint(0, 10)
    # paying users are more active
    if row['user_id'] in subscriptions['user_id'].values:
        activity_level += np.random.randint(5, 15)

    sampled_lessons = np.random.choice(lessons['lesson_id'].values, min(activity_level, 15), replace=False)
    for l_id in sampled_lessons:
        days_offset = np.random.randint(0, 20)
        user_lessons.append({
            'lesson_id': l_id,
            'user_id': row['user_id'],
            'completed_at': pd.to_datetime(row['registration_date'] + timedelta(days=days_offset)),
            'score': np.random.randint(60, 101)
        })

    if activity_level > 8:
        t_id = np.random.choice(tests['test_id'].values)
        days_offset = np.random.randint(5, 25)
        st_time = datetime.combine(row['registration_date'] + timedelta(days=days_offset),
                                   datetime.min.time()) + timedelta(hours=np.random.randint(8, 22))
        test_attempts.append({
            'attempt_id': attempt_id,
            'user_id': row['user_id'],
            'test_id': t_id,
            'started_at': st_time,
            'finished_at': st_time + timedelta(minutes=np.random.randint(60, 120)),
            'score': np.random.randint(100, 201),  # ZNO scale 100-200
            'max_score': 200
        })
        attempt_id += 1

user_lessons = pd.DataFrame(user_lessons)
test_attempts = pd.DataFrame(test_attempts)

# 7. Clickstream logs (raw data)
clickstream = []
ev_id = 900001
for idx, row in users.sample(n=1500).iterrows():  # generate logs for a part of the users, so the file does not blow up
    sess_id = f"sess_{np.random.randint(10000, 99999)}"
    base_time = datetime.combine(row['registration_date'], datetime.min.time()) + timedelta(hours=12)

    screens = ['Onboarding_1', 'Onboarding_2', 'Main_Dashboard', 'Lesson_List', 'Paywall']
    for i, screen in enumerate(screens):
        clickstream.append({
            'event_id': ev_id,
            'user_id': row['user_id'],
            'event_timestamp': base_time + timedelta(minutes=i * 2 + np.random.randint(0, 60)),
            'event_type': 'screen_view',
            'screen_name': screen,
            'session_id': sess_id
        })
        ev_id += 1
        # artificial log duplication bug (clickstream technical failure on 15 february)
        if row['registration_date'] == datetime(2026, 2, 15).date() and np.random.rand() < 0.5:
            clickstream.append({
                'event_id': ev_id,  # same one or incremented - let's increment it, but it is a duplicate in essence
                'user_id': row['user_id'],
                'event_timestamp': base_time + timedelta(minutes=i * 2),
                'event_type': 'screen_view',
                'screen_name': screen,
                'session_id': sess_id
            })
            ev_id += 1

clickstream_logs = pd.DataFrame(clickstream)

# saving to CSV (commented out, because the files are already generated and sit in data/ - so we do not overwrite them by accident)
# plans.to_csv('subscription_plans.csv', index=False)
# subjects.to_csv('subjects.csv', index=False)
# lessons.to_csv('lessons.csv', index=False)
# tests.to_csv('tests.csv', index=False)
# users.to_csv('users.csv', index=False)
# marketing_costs.to_csv('marketing_costs.csv', index=False)
# ab_test_segments.to_csv('ab_test_segments.csv', index=False)
# subscriptions.to_csv('subscriptions.csv', index=False)
# user_lessons.to_csv('user_lessons.csv', index=False)
# test_attempts.to_csv('test_attempts.csv', index=False)
# clickstream_logs.to_csv('clickstream_logs.csv', index=False)

print("All 11 tables created successfully in CSV format!")