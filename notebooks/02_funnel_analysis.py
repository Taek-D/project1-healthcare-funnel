import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats

print("="*60)
print("PROJECT 1: FUNNEL/COHORT/AARRR 분석")
print("="*60)

# ===============================================
# 1. 데이터 로드
# ===============================================
print("\n[Step 1] 데이터 로드 중...")

users_df = pd.read_csv('data/users.csv')
events_df = pd.read_csv('data/events.csv')
rewards_df = pd.read_csv('data/rewards.csv')

# 날짜 컬럼 변환
users_df['signup_date'] = pd.to_datetime(users_df['signup_date'])
events_df['event_date'] = pd.to_datetime(events_df['event_date'])
rewards_df['reward_date'] = pd.to_datetime(rewards_df['reward_date'])

print(f"✓ Users: {len(users_df):,}명")
print(f"✓ Events: {len(events_df):,}개")
print(f"✓ Rewards: {len(rewards_df):,}개")

# ===============================================
# 2. 사용자별 행동 데이터 병합
# ===============================================
print("\n[Step 2] 데이터 병합 중...")

# Pivot events
events_pivot = events_df.pivot_table(
    index='user_id',
    columns='event_type',
    values='event_date',
    aggfunc='min'
)

events_pivot.columns.name = None
events_pivot = events_pivot.reset_index()

# users와 병합
df_merged = users_df.merge(events_pivot, on='user_id', how='left')

# rewards 병합
df_merged = df_merged.merge(
    rewards_df[['user_id', 'reward_date', 'reward_amount']],
    on='user_id',
    how='left'
)

print(f"✓ 병합 완료: {len(df_merged):,}명의 통합 데이터")

# ===============================================
# 3. FUNNEL 분석
# ===============================================
print("\n" + "="*60)
print("📊 FUNNEL ANALYSIS")
print("="*60)

# Funnel 단계별 사용자 수 계산
stage_1_users = len(df_merged)
stage_2_users = df_merged['first_workout'].notna().sum()
stage_3_users = df_merged['first_reward'].notna().sum()
stage_4_users = df_merged['repeat_visit'].notna().sum()

funnel_data = {
    'Stage': ['1. 가입', '2. 첫운동', '3. 첫리워드', '4. 재방문'],
    'Users': [stage_1_users, stage_2_users, stage_3_users, stage_4_users]
}

funnel_df = pd.DataFrame(funnel_data)

# 전환율 계산 (첫 단계 대비)
funnel_df['Conversion Rate (%)'] = (
    funnel_df['Users'] / stage_1_users * 100
).round(2)

# 단계별 전환율 계산
funnel_df['Stage Conversion (%)'] = 0.0
for i in range(1, len(funnel_df)):
    if funnel_df['Users'].iloc[i-1] > 0:
        stage_conversion = (funnel_df['Users'].iloc[i] / funnel_df['Users'].iloc[i-1]) * 100
        funnel_df.at[i, 'Stage Conversion (%)'] = round(stage_conversion, 2)

print("\n[Funnel 결과]")
print(funnel_df.to_string(index=False))

# 통계
print(f"\n[핵심 지표]")
if stage_2_users > 0:
    print(f"✓ 가입 → 첫운동: {(stage_2_users/stage_1_users*100):.1f}%")
if stage_3_users > 0:
    print(f"✓ 첫운동 → 첫리워드: {(stage_3_users/stage_2_users*100):.1f}%")
if stage_4_users > 0:
    print(f"✓ 첫리워드 → 재방문: {(stage_4_users/stage_3_users*100):.1f}%")

print(f"✓ 전체 통과율: {(stage_4_users/stage_1_users*100):.1f}%")

# ===============================================
# 4. COHORT 분석
# ===============================================
print("\n" + "="*60)
print("📈 COHORT ANALYSIS")
print("="*60)

# Cohort 월 생성
df_merged['cohort_month'] = df_merged['signup_date'].dt.to_period('M')

# first_workout이 있을 때만 event_month 계산
df_merged['event_month'] = df_merged['first_workout'].dt.to_period('M')

# Cohort age 계산
df_merged['cohort_age'] = np.nan
mask = df_merged['event_month'].notna() & df_merged['cohort_month'].notna()
df_merged.loc[mask, 'cohort_age'] = (
    df_merged.loc[mask, 'event_month'].apply(lambda x: x.ordinal) - 
    df_merged.loc[mask, 'cohort_month'].apply(lambda x: x.ordinal)
)

# Cohort 테이블 생성
cohort_table = df_merged[df_merged['event_month'].notna()].groupby(
    ['cohort_month', 'cohort_age']
).size().reset_index(name='users')

# Pivot
cohort_pivot = cohort_table.pivot(index='cohort_month', columns='cohort_age', values='users')

# 리텐션율 계산
retention_table = cohort_pivot.divide(cohort_pivot.iloc[:, 0], axis=0) * 100

print("\n[Cohort 리텐션율 (%)]")
print(retention_table.round(1))

# CSV 저장
import os
if not os.path.exists('results'):
    os.makedirs('results')

retention_table.to_csv('results/cohort_retention.csv')
print(f"\n✓ 저장: results/cohort_retention.csv")

# ===============================================
# 5. AARRR 분석
# ===============================================
print("\n" + "="*60)
print("🎯 AARRR ANALYSIS")
print("="*60)

# 월별 데이터
df_merged['signup_month'] = df_merged['signup_date'].dt.to_period('M')

# 각 월별 AARRR 계산
aarrr_by_month = []

for month in sorted(df_merged['signup_month'].unique()):
    month_data = df_merged[df_merged['signup_month'] == month]
    
    aarrr_by_month.append({
        'Month': str(month),
        'Acquisition': len(month_data),
        'Activation': month_data['first_workout'].notna().sum(),
        'Retention': month_data['repeat_visit'].notna().sum(),
        'Revenue': month_data['reward_amount'].sum(),
        'Referral': len(month_data) // 10
    })

aarrr_df = pd.DataFrame(aarrr_by_month)

# 비율 계산
aarrr_df['Activation Rate (%)'] = (aarrr_df['Acquisition'] > 0).astype(int)
aarrr_df['Retention Rate (%)'] = (aarrr_df['Acquisition'] > 0).astype(int)

for i in range(len(aarrr_df)):
    if aarrr_df['Acquisition'].iloc[i] > 0:
        aarrr_df.at[i, 'Activation Rate (%)'] = round(
            aarrr_df['Activation'].iloc[i] / aarrr_df['Acquisition'].iloc[i] * 100, 2
        )
        aarrr_df.at[i, 'Retention Rate (%)'] = round(
            aarrr_df['Retention'].iloc[i] / aarrr_df['Acquisition'].iloc[i] * 100, 2
        )

aarrr_df['Avg Revenue Per User'] = (
    aarrr_df['Revenue'] / aarrr_df['Acquisition'].replace(0, 1)
).round(0)

print("\n[AARRR 결과 (월별)]")
print(aarrr_df[['Month', 'Acquisition', 'Activation', 'Retention', 'Revenue']].to_string(index=False))

# CSV 저장
aarrr_df.to_csv('results/aarrr_analysis.csv', index=False)
print(f"\n✓ 저장: results/aarrr_analysis.csv")

# ===============================================
# 6. 고급 분석: A/B Test
# ===============================================
print("\n" + "="*60)
print("🔬 A/B TEST: REWARD 효과")
print("="*60)

group_a = df_merged[df_merged['reward_date'].notna()]
group_b = df_merged[df_merged['reward_date'].isna()]

rate_a = (group_a['repeat_visit'].notna().sum() / len(group_a) * 100) if len(group_a) > 0 else 0
rate_b = (group_b['repeat_visit'].notna().sum() / len(group_b) * 100) if len(group_b) > 0 else 0

# 카이제곱 검정
group_a_repeat = group_a['repeat_visit'].notna().astype(int)
group_b_repeat = group_b['repeat_visit'].notna().astype(int)

contingency = pd.crosstab(
    pd.Series(['Reward']*len(group_a) + ['No Reward']*len(group_b)),
    pd.Series(list(group_a_repeat) + list(group_b_repeat))
)

chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

print(f"\n[A/B Test 결과]")
print(f"Group A (리워드 받음): {len(group_a):,}명, 재방문율 {rate_a:.2f}%")
print(f"Group B (리워드 못받음): {len(group_b):,}명, 재방문율 {rate_b:.2f}%")
print(f"\n차이: {rate_a - rate_b:.2f}%p")
print(f"P-value: {p_value:.6f}")

if p_value < 0.05:
    print(f"✓ 통계적으로 유의함 (p < 0.05)")
else:
    print(f"✗ 통계적으로 유의하지 않음 (p >= 0.05)")

# ===============================================
# 7. 시각화
# ===============================================
print("\n" + "="*60)
print("📊 시각화 생성 중...")
print("="*60)

# 한글 폰트 설정
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

# 1. Funnel Chart
fig, ax = plt.subplots(figsize=(10, 6))

colors = ['#FF6B6B', '#FFA500', '#4ECDC4', '#45B7D1']
bars = ax.barh(funnel_df['Stage'], funnel_df['Users'], color=colors)

for i, (bar, users) in enumerate(zip(bars, funnel_df['Users'])):
    width = bar.get_width()
    conversion = funnel_df['Conversion Rate (%)'].iloc[i]
    ax.text(width, bar.get_y() + bar.get_height()/2, 
            f'{int(users):,} ({conversion:.1f}%)',
            ha='left', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Number of Users', fontsize=12, fontweight='bold')
ax.set_title('Funnel Analysis: User Journey', fontsize=14, fontweight='bold')
ax.invert_yaxis()

plt.tight_layout()
plt.savefig('results/funnel_chart.png', dpi=300, bbox_inches='tight')
print("✓ Saved: results/funnel_chart.png")
plt.close()

# 2. Cohort Heatmap
fig, ax = plt.subplots(figsize=(14, 6))

cohort_heatmap = retention_table.iloc[:, :6]

sns.heatmap(cohort_heatmap, 
            annot=True, 
            fmt='.0f', 
            cmap='RdYlGn', 
            cbar_kws={'label': 'Retention Rate (%)'},
            ax=ax, 
            linewidths=0.5)

ax.set_title('Cohort Analysis: Monthly User Retention', fontsize=14, fontweight='bold')
ax.set_xlabel('Cohort Age (Months)', fontsize=12, fontweight='bold')
ax.set_ylabel('Cohort Month', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('results/cohort_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ Saved: results/cohort_heatmap.png")
plt.close()

# 3. AARRR Chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

aarrr_df_sorted = aarrr_df.sort_values('Month')
x_pos = range(len(aarrr_df_sorted))

ax1.plot(x_pos, aarrr_df_sorted['Acquisition'], marker='o', label='Acquisition', linewidth=2)
ax1.plot(x_pos, aarrr_df_sorted['Activation'], marker='s', label='Activation', linewidth=2)
ax1.plot(x_pos, aarrr_df_sorted['Retention'], marker='^', label='Retention', linewidth=2)

ax1.set_xlabel('Month', fontsize=11, fontweight='bold')
ax1.set_ylabel('Number of Users', fontsize=11, fontweight='bold')
ax1.set_title('AARRR: Monthly User Metrics', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(aarrr_df_sorted['Month'], rotation=45)

ax2.bar(x_pos, aarrr_df_sorted['Revenue'], color='#4ECDC4')
ax2.set_xlabel('Month', fontsize=11, fontweight='bold')
ax2.set_ylabel('Revenue (KRW)', fontsize=11, fontweight='bold')
ax2.set_title('AARRR: Monthly Revenue', fontsize=12, fontweight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(aarrr_df_sorted['Month'], rotation=45)

plt.tight_layout()
plt.savefig('results/aarrr_chart.png', dpi=300, bbox_inches='tight')
print("✓ Saved: results/aarrr_chart.png")
plt.close()

# 4. A/B Test Comparison
fig, ax = plt.subplots(figsize=(8, 5))

groups = ['With Reward\n(Group A)', 'Without Reward\n(Group B)']
rates = [rate_a, rate_b]
colors_ab = ['#4ECDC4', '#FF6B6B']

bars = ax.bar(groups, rates, color=colors_ab, alpha=0.8, edgecolor='black', linewidth=2)

for bar, rate in zip(bars, rates):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height,
            f'{rate:.2f}%',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_ylabel('Repeat Visit Rate (%)', fontsize=12, fontweight='bold')
ax.set_title(f'A/B Test: Reward Effect Analysis\n(p-value: {p_value:.6f})', fontsize=12, fontweight='bold')
ax.set_ylim(0, max(rates) * 1.2)

plt.tight_layout()
plt.savefig('results/ab_test_chart.png', dpi=300, bbox_inches='tight')
print("✓ Saved: results/ab_test_chart.png")
plt.close()

# ===============================================
# 8. 최종 요약
# ===============================================
print("\n" + "="*60)
print("✅ Analysis Complete!")
print("="*60)

print(f"\n[Generated Files]")
print(f"✓ results/funnel_chart.png")
print(f"✓ results/cohort_heatmap.png")
print(f"✓ results/aarrr_chart.png")
print(f"✓ results/ab_test_chart.png")
print(f"✓ results/cohort_retention.csv")
print(f"✓ results/aarrr_analysis.csv")

print(f"\n[Key Findings]")
print(f"1. Funnel: Signup → First Workout → First Reward → Repeat")
if stage_2_users > 0:
    print(f"   - Signup to First Workout: {(stage_2_users/stage_1_users*100):.1f}%")
if stage_4_users > 0:
    print(f"   - Overall Conversion: {(stage_4_users/stage_1_users*100):.1f}%")

print(f"\n2. Cohort: Monthly User Retention")
print(f"   - Avg Retention (Month 1): {retention_table.iloc[:, 1].mean():.1f}%")

print(f"\n3. AARRR: User Lifecycle")
print(f"   - Total Acquisition: {aarrr_df['Acquisition'].sum():,} users")
print(f"   - Avg Revenue Per User: {aarrr_df['Avg Revenue Per User'].mean():.0f} KRW")

print(f"\n4. A/B Test: Reward Effect")
if p_value < 0.05:
    print(f"   ✓ Reward significantly increases repeat visits!")
    print(f"   - Difference: {rate_a - rate_b:.2f}%p (statistically significant)")
else:
    print(f"   - No statistically significant difference")

print(f"\n[Next Steps]")
print(f"1. Create Tableau dashboard")
print(f"2. Upload to GitHub")
print(f"3. Add to portfolio")
