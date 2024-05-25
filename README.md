# Stable Diffusion 2D Game Asset Generator API

이 프로젝트는 Stable Diffusion 모델을 사용하여 2D 게임 에셋을 생성하는 FastAPI 백엔드 애플리케이션입니다. 사용자는 텍스트 프롬프트를 입력하여 이미지를 생성할 수 있으며, 프롬프트에 "2D game asset" 키워드를 추가하여 2D 게임 에셋을 생성할 수 있습니다.

## 요구 사항

- Python 3.7 이상
- pip

## 설치 방법

1. **저장소 클론**

    ```bash
    git clone https://github.com/yourusername/stable-diffusion-2d-game-asset-generator.git
    cd stable-diffusion-2d-game-asset-generator
    ```

2. **가상 환경 설정 및 활성화**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    .\venv\Scripts\activate  # Windows
    ```

3. **필요한 패키지 설치**

    ```bash
    pip install -r requirements.txt
    ```

## 환경 변수 설정

1. `.env` 파일을 프로젝트 루트 디렉토리에 생성하고, Hugging Face API 토큰을 추가합니다.

    ```
    HF_TOKEN=your_huggingface_token
    ```

## FastAPI 애플리케이션 실행

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000

