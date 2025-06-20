import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt

print("현재 작업 디렉토리:", os.getcwd())

# 1. 데이터 경로
data_path = './Sample/H001_ch01_20230922.csv'

# 2. CSV 데이터 불러오기
df = pd.read_csv(data_path)

# 3. 열 이름 확인 및 지정
if df.shape[1] >= 2:
    df.columns = ['time', 'W']
else:
    raise Exception("CSV 파일 구조가 예상과 다릅니다. 열이 2개 이상 필요합니다.")

print("데이터 미리보기:\n", df.head())

# 4. 전력 데이터만 추출
power = df['W'].values.reshape(-1, 1)

# 5. 스케일링
scaler = MinMaxScaler()
power_scaled = scaler.fit_transform(power)

# 6. LSTM 시퀀스 생성
timesteps = 30  # 30개 timestep 사용
X, y = [], []

for i in range(len(power_scaled) - timesteps):
    X.append(power_scaled[i:i+timesteps])
    y.append(power_scaled[i+timesteps])

X = np.array(X)
y = np.array(y)

print("LSTM 입력 데이터 shape:", X.shape)
print("LSTM 출력 데이터 shape:", y.shape)

# 7. Train/Test split (80%)
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# 8. LSTM 모델 정의
model = Sequential([
    LSTM(64, activation='tanh', input_shape=(timesteps, 1)),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse')
model.summary()

# 9. 학습
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

history = model.fit(X_train, y_train,
                    validation_data=(X_test, y_test),
                    epochs=20,
                    batch_size=32,
                    callbacks=[early_stop])

# 10. Loss 시각화
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.title('Loss Curve')
plt.show()

# 11. 예측
y_pred = model.predict(X_test)

# 12. 원래 스케일로 복원
y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))
y_pred_inv = scaler.inverse_transform(y_pred)

# 13. 결과 시각화
plt.figure(figsize=(10,4))
plt.plot(y_test_inv, label='True Power (W)')
plt.plot(y_pred_inv, label='Predicted Power (W)')
plt.title('True vs Predicted Power Consumption')
plt.legend()
plt.show()
