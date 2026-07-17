git clone https://github.com/B0kkl/malawi-verified-services-backend.git

cd malawi_verified_services_backend

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

python -m app.database.init_db

uvicorn app.main:app --reload
