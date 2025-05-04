import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function RequestsPage() {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    const response = await axios.get('http://127.0.0.1:8000/requests/');
    setRequests(response.data);
  };

  const handleDownloadExcel = () => {
    window.open('http://127.0.0.1:8000/export_excel/', '_blank');
  };


  return (
    <div className="stats-page">
      <h1>История Запросов</h1>

      <button onClick={handleDownloadExcel} className="download-button">
        Скачать статистику в Excel
      </button>

      {requests.map((req) => (
        <div key={req.id} className="request-card">
          <p><strong>Дата:</strong> {new Date(req.timestamp).toLocaleString()}</p>
          <p>Всего мест: {req.total_slots}</p>
          <p>Машин обнаружено: {req.cars_detected}</p>
          <p>Свободных мест: {req.empty_slots}</p>
          <img src={req.image_url} alt="Детектированное фото" />
        </div>
      ))}
    </div>
  );
}

export default RequestsPage;