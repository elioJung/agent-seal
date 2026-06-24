FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN printf '#!/bin/bash\nset -e\nalembic upgrade head\nexec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2\n' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
