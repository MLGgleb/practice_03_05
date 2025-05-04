import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function Home() {
  const [file, setFile] = useState(null);
  const [totalSlots, setTotalSlots] = useState(20); // по умолчанию 20
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSlotsChange = (e) => {
    setTotalSlots(Number(e.target.value));
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Выберите изображение');
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('total_slots', totalSlots);  // отправляем на сервер

    const response = await axios.post('http://127.0.0.1:8000/detect/', formData);

    setResult(response.data);
    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Парковка — поиск пустых мест</h1>

      <input type="file" onChange={handleFileChange} />

      <div>
        <label>Количество парковочных мест:</label>
        <input
          type="number"
          value={totalSlots}
          onChange={handleSlotsChange}
          min="1"
        />
      </div>

      <button onClick={handleUpload} className="button">
        {loading ? 'Обработка...' : 'Начать'}
      </button>

      {result && (
        <div className="result">
          <p>Обнаружено машин: {result.cars_detected}</p>
          <p>Свободных мест: {result.empty_slots}</p>
          <img src={result.image_url} alt="Результат" />
        </div>
      )}
    </div>
  );
}

export default Home;