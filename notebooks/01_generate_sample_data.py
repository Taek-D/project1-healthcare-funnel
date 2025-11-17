import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

print("=" * 50)
print("Project 1: 샘플 데이터 생성 시작")
print("=" * 50)

# ===============================================
# 1. 난수 시드 설정 (재현 가능성)
# ===============================================
np.random.seed(42)

# ===============================================
# 2. 기본 설정
# ===============================================
n_users = 50000  # 50,000명의 사용자
start_date = pd.Timestamp('2024-01-01')
end_date = pd.Timestamp('2024-12-31')

print(f"\n[설정]")
print(f"- 사용자 수: {n_users:,}명")
print(f"- 기간: {start_date.date()} ~ {end_date.date()}")

# ===============================================
# 3. 사용자 기본 정보 생성
# ===============================================
print(f"\n[Step 1] 사용자 기본 정보 생성 중...")

# 가입 날짜 범위 내 랜덤 생성
date_range = (end_date - start_date).days
signup_dates = [start_date + timedelta(days=int(x)) for x in np.random.uniform(0, date_range, n_users)]

users_df = pd.DataFrame({
    'user_id': range(1, n_users + 1),
    'signup_date': signup_dates,
    'age': np.random.randint(18, 65, n_users),
    'gender': np.random.choice(['M', 'F'], n_users),
    'region': np.random.choice(['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon'], n_users)
})

print(f"✓ 완료: {len(users_df):,}명의 사용자 생성")
print(f"\n사용자 데이터 샘플:")
print(users_df.head())

# ===============================================
# 4. 앱 사용 이벤트 생성
# ===============================================
print(f"\n[Step 2] 앱 사용 이벤트 생성 중...")

events_list = []
conversion_tracking = {
    'signup': 0,
    'first_workout': 0,
    'first_reward': 0,
    'repeat_visit': 0
}

for idx, row in users_df.iterrows():
    user_id = row['user_id']
    signup_date = row['signup_date']  # 이미 pd.Timestamp
    conversion_tracking['signup'] += 1
    
    # ===== Funnel 단계 1: 첫 운동 =====
    # 80% 사용자가 첫 운동 시작
    if np.random.random() < 0.80:
        conversion_tracking['first_workout'] += 1
        
        # 첫 운동까지의 일수 (대부분 7일 이내)
        days_to_first_workout = np.random.randint(1, 8)
        first_workout_date = signup_date + timedelta(days=days_to_first_workout)
        
        events_list.append({
            'user_id': user_id,
            'event_type': 'first_workout',
            'event_date': first_workout_date,
            'event_time': first_workout_date + timedelta(hours=np.random.randint(0, 24))
        })
        
        # ===== Funnel 단계 2: 첫 리워드 =====
        # 75% 사용자가 리워드 수령
        if np.random.random() < 0.75:
            conversion_tracking['first_reward'] += 1
            
            # 첫 운동 후 1-2일 안에 리워드 수령
            days_to_reward = np.random.randint(1, 3)
            first_reward_date = first_workout_date + timedelta(days=days_to_reward)
            
            events_list.append({
                'user_id': user_id,
                'event_type': 'first_reward',
                'event_date': first_reward_date,
                'event_time': first_reward_date + timedelta(hours=np.random.randint(0, 24))
            })
            
            # ===== Funnel 단계 3: 재방문 =====
            # 60% 사용자가 7일 이내 재방문
            if np.random.random() < 0.60:
                conversion_tracking['repeat_visit'] += 1
                
                # 리워드 수령 후 1-7일 내 재방문
                days_to_repeat = np.random.randint(1, 8)
                repeat_date = first_reward_date + timedelta(days=days_to_repeat)
                
                events_list.append({
                    'user_id': user_id,
                    'event_type': 'repeat_visit',
                    'event_date': repeat_date,
                    'event_time': repeat_date + timedelta(hours=np.random.randint(0, 24))
                })

events_df = pd.DataFrame(events_list)

print(f"✓ 완료: {len(events_df):,}개의 이벤트 생성")
print(f"\n이벤트 타입별 개수:")
print(events_df['event_type'].value_counts())

print(f"\n[Conversion Tracking]")
print(f"- Signup: {conversion_tracking['signup']:,}명 (100%)")
print(f"- First Workout: {conversion_tracking['first_workout']:,}명 ({conversion_tracking['first_workout']/conversion_tracking['signup']*100:.1f}%)")
print(f"- First Reward: {conversion_tracking['first_reward']:,}명 ({conversion_tracking['first_reward']/conversion_tracking['first_workout']*100:.1f}% of Workout)")
print(f"- Repeat Visit: {conversion_tracking['repeat_visit']:,}명 ({conversion_tracking['repeat_visit']/conversion_tracking['first_reward']*100:.1f}% of Reward)")

# ===============================================
# 5. 리워드 지급 기록 생성
# ===============================================
print(f"\n[Step 3] 리워드 지급 기록 생성 중...")

rewards_list = []

for _, row in events_df[events_df['event_type'] == 'first_reward'].iterrows():
    # 리워드 금액: 1,000원 ~ 10,000원
    reward_amount = np.random.randint(10, 100) * 100  # 1,000원 단위
    
    rewards_list.append({
        'user_id': row['user_id'],
        'reward_date': row['event_date'],
        'reward_amount': reward_amount
    })

rewards_df = pd.DataFrame(rewards_list)

print(f"✓ 완료: {len(rewards_df):,}개의 리워드 지급 기록 생성")
print(f"\n리워드 통계:")
print(f"- 총 지급액: {rewards_df['reward_amount'].sum():,}원")
print(f"- 평균 리워드: {rewards_df['reward_amount'].mean():.0f}원")
print(f"- 최대/최소: {rewards_df['reward_amount'].max()}원 / {rewards_df['reward_amount'].min()}원")

# ===============================================
# 6. CSV 파일 저장
# ===============================================
print(f"\n[Step 4] CSV 파일 저장 중...")

data_dir = 'data'

# 디렉토리 없으면 생성
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# CSV 저장
users_df.to_csv(f'{data_dir}/users.csv', index=False, encoding='utf-8')
events_df.to_csv(f'{data_dir}/events.csv', index=False, encoding='utf-8')
rewards_df.to_csv(f'{data_dir}/rewards.csv', index=False, encoding='utf-8')

print(f"✓ 저장 완료:")
print(f"  - data/users.csv ({len(users_df):,} rows)")
print(f"  - data/events.csv ({len(events_df):,} rows)")
print(f"  - data/rewards.csv ({len(rewards_df):,} rows)")

# ===============================================
# 7. 데이터 검증
# ===============================================
print(f"\n[Step 5] 데이터 검증...")

print(f"\n[Users 데이터 샘플]")
print(users_df.head())
print(f"\nUsers 정보:")
print(users_df.info())

print(f"\n[Events 데이터 샘플]")
print(events_df.head())
print(f"\nEvents 정보:")
print(events_df.info())

print(f"\n[Rewards 데이터 샘플]")
print(rewards_df.head())
print(f"\nRewards 정보:")
print(rewards_df.info())

# ===============================================
# 8. 데이터 품질 체크
# ===============================================
print(f"\n[데이터 품질 체크]")

# 중복 user_id 확인
duplicate_users = users_df['user_id'].duplicated().sum()
print(f"- Users 중복: {duplicate_users}개 ✓" if duplicate_users == 0 else f"- Users 중복: {duplicate_users}개 ✗")

# 결측치 확인
missing_values = users_df.isnull().sum().sum()
print(f"- Users 결측치: {missing_values}개 ✓" if missing_values == 0 else f"- Users 결측치: {missing_values}개 ✗")

print(f"\n{'='*50}")
print(f"✅ 샘플 데이터 생성 완료!")
print(f"{'='*50}")
