import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

pd.options.display.max_columns = None
pd.set_option('display.width', 9999)

ab_test_segments = pd.read_csv('data/ab_test_segments.csv')
users = pd.read_csv('data/users.csv')
subscriptions = pd.read_csv('data/subscriptions.csv')
subscription_plans = pd.read_csv('data/subscription_plans.csv')
subjects = pd.read_csv('data/subjects.csv')
lessons = pd.read_csv('data/lessons.csv')
tests = pd.read_csv('data/tests.csv')
marketing_costs = pd.read_csv('data/marketing_costs.csv')
user_lessons = pd.read_csv('data/user_lessons.csv')
test_attempts = pd.read_csv('data/test_attempts.csv')
clickstream_logs = pd.read_csv('data/clickstream_logs.csv')

# print(ab_test_segments.info())
# print(ab_test_segments.head())
#
# print(users.info())
# print(users.head())
#
# print('subscriptions')
# print(subscriptions.info())
# print(subscriptions.head())
#
# print('subscription_plans')
# print(subscription_plans.info())
# print(subscription_plans.head())
#
# print(subjects.info())
# print(subjects.head())
#
# print(lessons.info())
# print(lessons.head())
#
# print(tests.info())
# print(tests.head())
#
# print(marketing_costs.info())
# print(marketing_costs.head())
#
# print(user_lessons.info())
# print(user_lessons.head())
#
# print(test_attempts.info())
# print(test_attempts.head())
#
# print(clickstream_logs.info())
# print(clickstream_logs.head())

######################################################################################################################## ab test

users_ab_test = users.merge(ab_test_segments, on = 'user_id')

# let's check the platform split for the different groups
sns.countplot(x = 'platform', data = users_ab_test, hue= 'variant')
plt.show()

##let's check the acquisition split for the different groups
sns.countplot(x = 'marketing_channel', data = users_ab_test, hue = 'variant')
plt.show()

##overall split of the tested users
users_ab_test_summarized = users_ab_test.value_counts('variant').reset_index()
print(users_ab_test_summarized)
users_ab_test_summarized.plot(x = 'variants', y = 'count', kind = 'pie')
plt.show()

users_ab_test_subscription = users_ab_test.merge(subscriptions, on = 'user_id', how = 'left')
print(users_ab_test_subscription)
users_ab_test_subscription_a = users_ab_test_subscription[users_ab_test_subscription['variant'] == 'A']
users_ab_test_subscription_b = users_ab_test_subscription[users_ab_test_subscription['variant'] == 'B']

cra = users_ab_test_subscription_a['subscription_id'].count() / users_ab_test_subscription_a['user_id'].count()
crb = users_ab_test_subscription_b['subscription_id'].count() / users_ab_test_subscription_b['user_id'].count()

print(f'cra : {cra}')
print(f'crb : {crb}')

pa = cra
pb = crb
# z-test on the difference of proportions (conversions) between the variants
ppool = (users_ab_test_subscription_a['subscription_id'].count() + users_ab_test_subscription_b['subscription_id'].count())/ (users_ab_test_subscription_a['user_id'].count() + users_ab_test_subscription_b['user_id'].count())
SEppool = np.sqrt(ppool*(1-ppool)*(1/users_ab_test_subscription_a['user_id'].count() + 1/users_ab_test_subscription_b['user_id'].count()))
z = (cra - crb)/SEppool
if z > 1.96 :
    print(f'feature a statistically significant, z-score = {z}')
if z <= 1.96 :
    print(f'bad feature a, z-score = {z}')

# different segments for a
cra_by_cohorts = users_ab_test_subscription_a.groupby(['platform','marketing_channel'])[['user_id','subscription_id']].count().reset_index()
cra_by_cohorts['cr'] = cra_by_cohorts['subscription_id'] / cra_by_cohorts['user_id']
print(cra_by_cohorts)

# different segments for b
crb_by_cohorts = users_ab_test_subscription_b.groupby(['platform','marketing_channel'])[['user_id','subscription_id']].count().reset_index()
crb_by_cohorts['cr'] = crb_by_cohorts['subscription_id'] / crb_by_cohorts['user_id']
print(crb_by_cohorts)

# different segments for the whole population
cr_by_cohorts  = users_ab_test_subscription.groupby(['platform','marketing_channel'])[['user_id','subscription_id']].count().reset_index()
cr_by_cohorts['cr'] = cr_by_cohorts['subscription_id'] / cr_by_cohorts['user_id']
print(cr_by_cohorts)

# cr by channel
cr_by_marketing_channel = users_ab_test_subscription.groupby('marketing_channel')[['user_id','subscription_id']].count().reset_index()
cr_by_marketing_channel['cr'] = cr_by_marketing_channel['subscription_id'] / cr_by_marketing_channel['user_id']
print(cr_by_marketing_channel)

# cr by platform
cr_by_platform = users_ab_test_subscription.groupby('platform')[['user_id','subscription_id']].count().reset_index()
cr_by_platform['cr'] = cr_by_platform['subscription_id'] / cr_by_platform['user_id']
print(cr_by_platform)

Na = users_ab_test_subscription_a['user_id'].count()
Nb = users_ab_test_subscription_b['user_id'].count()

## bootstrap over 10000 iterations for the confidence interval of the conversion difference

diff_distribution = []

for i in range(10000):
    sample_a = users_ab_test_subscription_a.sample(n = Na,replace = True)
    sample_b = users_ab_test_subscription_b.sample(n=Nb, replace = True)
    cra_sample = sample_a['subscription_id'].count() / sample_a['user_id'].count()
    crb_sample = sample_b['subscription_id'].count() / sample_b['user_id'].count()
    diff = cra_sample - crb_sample
    diff_distribution.append(diff)

diff_distribution.sort()
quantile250 = diff_distribution[250]
quantile9750 = diff_distribution[9750]

plt.hist(diff_distribution)
plt.axvline(quantile250, color='red', linestyle='--', label=f'quantile250 = {quantile250:.4f}')
plt.legend()
plt.show()

print(quantile250, quantile9750)