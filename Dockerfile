# Gunakan image Python resmi sebagai base image
FROM python:3.11-slim

# Set working directory di dalam container
WORKDIR /app

# Copy requirements.txt dan install dependencies
# Gunakan --no-cache-dir untuk menghemat ruang disk
# Gunakan -r untuk menginstal dari file requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode aplikasi ke dalam container
COPY . .

# Expose port yang akan digunakan oleh FastAPI (default Uvicorn adalah 8000)
EXPOSE 8000

# Command untuk menjalankan aplikasi menggunakan Uvicorn
# --host 0.0.0.0 agar dapat diakses dari luar container
# --reload (opsional, hanya untuk pengembangan)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
