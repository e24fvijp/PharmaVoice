FROM python:3.10-slim

# 必要なビルドツールをインストール
RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3-dev \
    portaudio19-dev \
    libsndfile1 \
    alsa-utils \
    libasound2-dev \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを作成
WORKDIR /app

# requirements.txtをコピー
COPY requirements.txt .

# 必要なパッケージをインストール
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポートの公開
EXPOSE 8501

# Streamlitアプリを実行
CMD ["streamlit", "run", "recording.py", "--server.port=8501", "--server.address=0.0.0.0"]