import { useState } from "react";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");

  const register = async () => {
    const res = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (res.ok) alert("Usuario registrado correctamente");
    else alert("Error al registrar");
  };

  const login = async () => {
    const res = await fetch("http://localhost:8000/auth/jwt/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: email, password }),
    });

    if (res.ok) {
      const data = await res.json();
      setToken(data.access_token);
      alert("Login exitoso");
    } else alert("Error al iniciar sesión");
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      {!token ? (
        <div className="bg-white p-10 rounded-xl shadow-lg w-96 flex flex-col gap-4">
          <h1 className="text-2xl font-bold text-center">Bienvenido</h1>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="border p-2 rounded"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="border p-2 rounded"
          />
          <div className="flex gap-2">
            <button
              onClick={register}
              className="flex-1 bg-green-500 text-white py-2 rounded hover:bg-green-600 transition"
            >
              Registrarse
            </button>
            <button
              onClick={login}
              className="flex-1 bg-blue-500 text-white py-2 rounded hover:bg-blue-600 transition"
            >
              Login
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white p-10 rounded-xl shadow-lg w-96 text-center">
          <h2 className="text-xl font-bold mb-2">Bienvenido!</h2>
          <p className="mb-2">Tu token JWT:</p>
          <code className="block bg-gray-200 p-2 rounded break-words">
            {token}
          </code>
        </div>
      )}
    </div>
  );
}

export default App;
