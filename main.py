from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import torch
import pandas as pd
import uuid
import os
import glob
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загружаем YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Папка static
os.makedirs("static", exist_ok=True)

# Настройка базы данных
DATABASE_URL = "sqlite:///./parking.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Модель базы данных
class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_slots = Column(Integer)
    cars_detected = Column(Integer)
    empty_slots = Column(Integer)
    image_url = Column(String)

# Создаём таблицы
Base.metadata.create_all(bind=engine)

@app.post("/detect/")
async def detect_parking(
    file: UploadFile = File(...),
    total_slots: int = Form(20)
):
    temp_input = f"static/input_{uuid.uuid4()}.jpg"
    with open(temp_input, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    results = model(temp_input)
    results.save()

    latest_folder = sorted(glob.glob('runs/detect/*'), key=os.path.getmtime)[-1]
    detected_file = glob.glob(os.path.join(latest_folder, '*.jpg'))[0]

    output_filename = f"result_{uuid.uuid4()}.jpg"
    output_path = os.path.join("static", output_filename)
    shutil.copyfile(detected_file, output_path)

    detected_objects = results.pandas().xyxy[0]
    cars_detected = detected_objects[detected_objects['name'] == 'car']
    num_cars = len(cars_detected)
    empty_slots = max(total_slots - num_cars, 0)

    os.remove(temp_input)

    image_url = f"http://127.0.0.1:8000/static/{output_filename}"

    # Сохраняем запрос в базу данных
    db = SessionLocal()
    request_entry = Request(
        total_slots=total_slots,
        cars_detected=num_cars,
        empty_slots=empty_slots,
        image_url=image_url
    )
    db.add(request_entry)
    db.commit()
    db.close()

    return {
        "total_slots": total_slots,
        "cars_detected": num_cars,
        "empty_slots": empty_slots,
        "image_url": image_url
    }

@app.get("/static/{filename}")
async def get_image(filename: str):
    return FileResponse(f"static/{filename}")

# Новый эндпоинт для получения всех запросов
@app.get("/requests/")
async def get_requests():
    db = SessionLocal()
    requests_list = db.query(Request).order_by(Request.timestamp.desc()).all()
    db.close()
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "total_slots": r.total_slots,
            "cars_detected": r.cars_detected,
            "empty_slots": r.empty_slots,
            "image_url": r.image_url
        }
        for r in requests_list
    ]

@app.get("/export_excel/")
async def export_excel():
    db = SessionLocal()
    requests_list = db.query(Request).order_by(Request.timestamp.desc()).all()
    db.close()

    data = [
        {
            "ID": r.id,
            "Дата": r.timestamp.isoformat(),
            "Всего мест": r.total_slots,
            "Машин обнаружено": r.cars_detected,
            "Свободных мест": r.empty_slots,
            "Ссылка на картинку": r.image_url
        }
        for r in requests_list
    ]

    df = pd.DataFrame(data)
    excel_path = "static/parking_stats.xlsx"
    df.to_excel(excel_path, index=False)

    return FileResponse(excel_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="parking_stats.xlsx")
