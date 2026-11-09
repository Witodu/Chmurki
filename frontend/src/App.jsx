import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = "http://localhost:8000";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [isRegistering, setIsRegistering] = useState(false); // Stan przełączający na rejestrację
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    if (token) {
      axios.get(`${API_URL}/files`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => setFiles(res.data))
      .catch(err => {
        console.error(err);
        if (err.response?.status === 401) logout();
      });
    }
  }, [token]);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_URL}/login`, { login, password });
      setToken(res.data.token);
      localStorage.setItem("token", res.data.token);
    } catch (err) {
      alert("Błąd logowania: Nieprawidłowy login lub hasło");
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/register`, { login, password });
      alert("Konto zostało utworzone! Możesz się teraz zalogować.");
      setIsRegistering(false);
      setPassword("");
    } catch (err) {
      // Wyświetli dokładny komunikat z backendu (np. "Login jest zajęty")
      const msg = err.response?.data?.detail || "Błąd podczas rejestracji";
      alert(`Błąd: ${msg}`);
    }
  };

  const logout = () => {
    setToken("");
    localStorage.removeItem("token");
    setFiles([]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      await axios.post(`${API_URL}/files`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data"
        }
      });
      alert("Plik przesłany pomyślnie!");
      window.location.reload();
    } catch (err) {
      alert("Błąd podczas przesyłania pliku.");
    }
  };

  const downloadFile = async (fileId, fileName) => {
    try {
      const res = await axios.get(`${API_URL}/files/${fileId}/download`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401) logout();
      alert("Błąd podczas pobierania pliku.");
    }
  };

  if (!token) {
    return (
      <div style={{ padding: "40px", fontFamily: "sans-serif" }}>
        <h2>{isRegistering ? "Rejestracja nowego konta" : "Logowanie do Systemu Chmurowego"}</h2>
        
        <form onSubmit={isRegistering ? handleRegister : handleLogin}>
          <div>
            <label>Login: </label>
            <input type="text" value={login} onChange={e => setLogin(e.target.value)} required />
          </div>
          <div style={{ marginTop: "10px" }}>
            <label>Hasło: </label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <button type="submit" style={{ marginTop: "15px" }}>
            {isRegistering ? "Zarejestruj się" : "Zaloguj się"}
          </button>
        </form>

        <p style={{ marginTop: "20px" }}>
          {isRegistering ? "Masz już konto?" : "Nie masz jeszcze konta?"}{" "}
          <button 
            onClick={() => setIsRegistering(!isRegistering)} 
            style={{ background: "none", border: "none", color: "blue", cursor: "pointer", textDecoration: "underline" }}
          >
            {isRegistering ? "Przejdź do logowania" : "Zarejestruj się"}
          </button>
        </p>
      </div>
    );
  }

  return (
    <div style={{ padding: "40px", fontFamily: "sans-serif" }}>
      <h2>Panel Użytkownika Chmury</h2>
      <button onClick={logout}>Wyloguj się</button>

      <hr style={{ margin: "20px 0" }} />

      <h3>Prześlij nowy plik</h3>
      <form onSubmit={handleUpload}>
        <input type="file" onChange={e => setSelectedFile(e.target.files[0])} />
        <button type="submit">Wyślij</button>
      </form>

      <hr style={{ margin: "20px 0" }} />

      <h3>Twoje pliki w chmurze</h3>
      <table border="1" cellPadding="10" style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th>Nazwa</th>
            <th>Rozmiar (bajty)</th>
            <th>Wersja</th>
            <th>Data przesłania</th>
            <th>Akcje</th>
          </tr>
        </thead>
        <tbody>
          {files.map(f => (
            <tr key={f.id}>
              <td>{f.name}</td>
              <td>{f.size}</td>
              <td>v.{f.version}</td>
              <td>{new Date(f.date).toLocaleString()}</td>
              <td>
                <button
                  onClick={() => downloadFile(f.id, f.name)}
                  style={{ marginRight: "5px", padding: "5px 10px", cursor: "pointer" }}
                >
                  Pobierz
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}