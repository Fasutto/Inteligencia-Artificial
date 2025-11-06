import React, { useState, useRef } from 'react';
import axios from 'axios';
import './App.css';

/*
  App.jsx - Interfaz principal del front-end
  - Maneja login por userId
  - Muestra películas valoradas por el usuario (scroll)
  - Muestra recomendaciones y permite valorar (1-5)
  - Contiene autocomplete con debounce
*/

function RatingCell({ movieId, userId, onRated, setError }) {
  // Componente que renderiza el selector de puntuación y el botón
  const [value, setValue] = useState(4); // rating por defecto
  const [loading, setLoading] = useState(false); // flag de envío

  const submit = async () => {
    // Valida que el usuario esté logueado y que la película tenga id
    if (!userId) { setError('Inicia sesión para valorar'); return; }
    if (!movieId) { setError('movieId desconocido'); return; }
    setLoading(true);
    try {
      // Envia POST /rate al backend con userId, movieId y rating
      const res = await axios.post('http://127.0.0.1:5000/rate', { userId: userId, movieId: movieId, rating: value });
      if (res.data) {
        // Se pasa al padre tanto la respuesta completa como un objeto meta con la película y la puntuación enviada. El padre decide cómo actualizar la UI (optimistic update o reemplazo usando res.data).
        onRated(res.data, { movieId: movieId, rating: value });
      }
    } catch (err) {
      setError('Error al enviar valoración');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{display:'flex', gap:8, alignItems:'center'}}>
      <select value={value} onChange={(e)=>setValue(parseInt(e.target.value))} disabled={!userId || loading}>
        <option value={1}>1</option>
        <option value={2}>2</option>
        <option value={3}>3</option>
        <option value={4}>4</option>
        <option value={5}>5</option>
      </select>
      <button onClick={submit} disabled={!userId || loading}>{loading ? 'Enviando...' : 'Valorar'}</button>
    </div>
  )
}

function App() {
  // Estados principales del componente
  const [userId, setUserId] = useState(''); // input de login (texto)
  const [loggedUser, setLoggedUser] = useState(null); // userId validado (number)
  const [ratedMovies, setRatedMovies] = useState([]); // lista de películas valoradas por el user

  // Estados para búsqueda y recomendaciones
  const [movie, setMovie] = useState(''); // texto del buscador
  const [recommendations, setRecommendations] = useState([]); // recomendaciones mostradas
  const [error, setError] = useState(''); // mensaje de error global
  const [suggestions, setSuggestions] = useState([]); // lista de autocomplete
  const [showSuggestions, setShowSuggestions] = useState(false); // si se muestran sugerencias
  const [suggestionsLoading, setSuggestionsLoading] = useState(false); // loader sugerencias
  const [recommendationsLoading, setRecommendationsLoading] = useState(false); // loader recomendaciones
  const [highlightIndex, setHighlightIndex] = useState(-1); // navegación con teclado
  const debounceRef = useRef(null); // referencia para debounce
  const cancelTokenRef = useRef(null); // cancel token para axios

  const fetchRecommendations = async () => {
    if (!movie) {
      setError('Por favor, ingresa el nombre de una película.');
      return;
    }
    try {
      setRecommendations([]);
      setError('');
      setRecommendationsLoading(true);
      const response = await axios.get(`http://127.0.0.1:5000/recommend/${encodeURIComponent(movie)}`);
      if (response.data.length === 0) {
        setError(`No se encontraron recomendaciones para "${movie}". ¿Revisaste la ortografía?`);
      } else {
        setRecommendations(response.data);
      }
    } catch (err) {
      setError('Error al conectar con el servidor. ¿Está el backend en ejecución?');
    } finally {
      setRecommendationsLoading(false);
    }
  };

  // fetchRecommendations: pide al backend recomendaciones basadas en el título y actualiza el estado `recommendations`. Muestra errores cuando no hay resultados o el backend no responde.

  const fetchUserData = async (uid) => {
    if (!uid) return;
    try {
      // Películas valoradas por el usuario.
      const ratedRes = await axios.get(`http://127.0.0.1:5000/user/${uid}/rated`);
      setRatedMovies(ratedRes.data || []);
      // Recomendaciones personalizadas (CF).
      setRecommendations([]);
      setRecommendationsLoading(true);
      const recRes = await axios.get(`http://127.0.0.1:5000/recommend_user/${uid}`);
      setRecommendations(recRes.data || []);
    } catch (err) {
      setError('Error al obtener datos del usuario. ¿Está el backend en ejecución?');
    } finally {
      setRecommendationsLoading(false);
    }
  };

  // fetchUserData: obtiene las películas valoradas por `uid` y las recomendaciones personalizadas (CF). Actualiza `ratedMovies` y `recommendations`.

  const handleLogin = () => {
    const uid = parseInt(userId);
    if (isNaN(uid)) { setError('Ingresa un userId numérico'); return; }
    // Valida que el usuario exista en el backend.
    axios.get(`http://127.0.0.1:5000/user_exists/${uid}`).then(res => {
      if (res.data && res.data.exists) {
        setLoggedUser(uid);
        setError('');
        fetchUserData(uid);
      } else {
        setError('Usuario no existente');
        setLoggedUser(null);
      }
    }).catch(err => {
      setError('Error al validar usuario');
    });
  };

  // handleLogin: valida que el userId exista en el backend y, si existe, marca al usuario como "logueado" y carga sus datos.

  const fetchSuggestions = (q) => {
    // Limpia sugerencias previas y timers.
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (cancelTokenRef.current) cancelTokenRef.current.cancel('cancel previous');
    if (!q || q.length < 2) { setSuggestions([]); setShowSuggestions(false); return; }

    debounceRef.current = setTimeout(async () => {
      cancelTokenRef.current = axios.CancelToken.source();
      setSuggestionsLoading(true);
      try {
        const res = await axios.get(`http://127.0.0.1:5000/search/autocomplete/${encodeURIComponent(q)}`, { cancelToken: cancelTokenRef.current.token });
        setSuggestions(res.data || []);
        setShowSuggestions(true);
      } catch (err) {
        if (!axios.isCancel(err)) console.error(err);
      } finally {
        setSuggestionsLoading(false);
      }
    }, 250);
  };

  // fetchSuggestions: obtiene sugerencias de títulos usando debounce para evitar llamar al backend en cada pulsación. Usa cancel tokens para abortar peticiones anteriores si el usuario sigue escribiendo.

  const selectSuggestion = (s) => {
    const val = typeof s === 'string' ? s : (s.title || s);
    setMovie(val);
    setShowSuggestions(false);
    // Ejecutar la búsqueda inmediatamente al seleccionar la sugerencia
    fetchRecommendations();
  };

  // selectSuggestion: cuando el usuario selecciona una sugerencia, la coloca en l input y lanza la búsqueda de recomendaciones por contenido.

  return (
    <div className="App">
      <header className="App-header">
        <h1>Sistema de Recomendación de Películas</h1>
        <div className="user-login">
          <input type="text" placeholder="Ingresa tu userId (ej. 1)" value={userId} onChange={(e)=>setUserId(e.target.value)} />
          <button onClick={handleLogin}>Iniciar sesión</button>
          {loggedUser && <span style={{marginLeft:10}}>Conectado como usuario {loggedUser} <button onClick={()=>{setLoggedUser(null); setRatedMovies([]); setRecommendations([]);}}>Cerrar sesión</button></span>}
        </div>

        {/* Películas valoradas por el usuario */}
        {loggedUser && (
          <div className="rated-movies">
            <h3>Películas valoradas por el usuario {loggedUser}:</h3>
            {ratedMovies.length === 0 ? <p>No hay valoraciones.</p> : (
              <div className="rated-table-wrapper">
                <table className="rated-table">
                  <thead>
                    <tr>
                      <th>Nombre</th>
                      <th>Año</th>
                      <th>Géneros</th>
                      <th>Puntuación</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ratedMovies.map((m, i) => {
                      // Extrae el año del título si está entre paréntesis.
                      const yearMatch = (m.title || '').match(/\((\d{4})\)$/);
                      const year = yearMatch ? yearMatch[1] : '';
                      const rowKey = m && m.movieId ? `rated-${m.movieId}` : `rated-${i}`;
                      return (
                        <tr key={rowKey}>
                          <td>{m.title}</td>
                          <td>{year}</td>
                          <td>{m.genres}</td>
                          <td>{m.rating}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
        <div className="search-box" style={{ position: 'relative' }}>
          <input
            type="text"
            placeholder="Escribe una película que te guste..."
            value={movie}
            onChange={(e) => { setMovie(e.target.value); fetchSuggestions(e.target.value); setHighlightIndex(-1); }}
            onKeyDown={(e) => {
              if (!showSuggestions) return;
              if (e.key === 'ArrowDown') { e.preventDefault(); setHighlightIndex(i => Math.min(i + 1, suggestions.length - 1)); }
              else if (e.key === 'ArrowUp') { e.preventDefault(); setHighlightIndex(i => Math.max(i - 1, 0)); }
              else if (e.key === 'Enter') {
                if (highlightIndex >= 0 && highlightIndex < suggestions.length) {
                  e.preventDefault(); const s = suggestions[highlightIndex]; selectSuggestion(typeof s === 'string' ? s : (s.title || s));
                } else {
                  fetchRecommendations();
                }
              }
            }}
            onKeyPress={(e) => e.key === 'Enter' && fetchRecommendations()}
            onFocus={() => { if (suggestions.length) setShowSuggestions(true); }}
          />
          {suggestionsLoading && <span className="loader" aria-hidden="true"></span>}
          <button onClick={fetchRecommendations}>
            Obtener Recomendaciones
          </button>

          {showSuggestions && suggestions.length > 0 && (
            <ul className="suggestions-list">
              {suggestions.map((s, i) => {
                const text = typeof s === 'string' ? s : (s.title || s);
                return (
                  <li key={i}
                      className={i === highlightIndex ? 'active' : ''}
                      onMouseDown={() => selectSuggestion(text)}
                      onMouseEnter={() => setHighlightIndex(i)}
                  >
                    {text}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
        {error && <p className="error-message">{error}</p>}
        <div className="recommendations-list">
          {recommendationsLoading && <div className="recommendations-loading"><span className="loader"/></div>}
          {recommendations.length > 0 && <h2>Recomendaciones para ti:</h2>}
          {recommendations.length > 0 && (
            <table className="recommendations-table">
              <thead>
                <tr><th>Nombre</th><th>Año</th><th>Géneros</th><th>Valorar</th></tr>
              </thead>
              <tbody>
                {recommendations.map((rec) => {
                  const title = rec.title || rec;
                  const yearMatch = (title || '').match(/\((\d{4})\)$/);
                  const year = yearMatch ? yearMatch[1] : '';
                  const genres = rec.genres || '';
                  const mid = rec.movieId || null;
                  const rowKey = mid != null ? `rec-${mid}` : `rec-${title}`;
                  return (
                    <tr key={rowKey}>
                      <td>{title}</td>
                      <td>{year}</td>
                      <td>{genres}</td>
                      <td>
                        <RatingCell movieId={mid} userId={loggedUser} onRated={(data, meta)=>{
                          // Actualiza la lista de películas valoradas si el backend devolvió la lista completa.
                          // Si no, hace un optimistic update usando el objeto meta con movieId, title, genres y rating.
                          if (data && data.rated) setRatedMovies(data.rated);
                          else if (meta && meta.movieId) {
                            const ratedObj = {
                              movieId: meta.movieId,
                              title: title,
                              genres: genres,
                              rating: meta.rating,
                            };
                            setRatedMovies(prev => {
                              // Remplaza si ya existía, o añade al inicio.
                              const existsIdx = prev.findIndex(r => Number(r.movieId) === Number(meta.movieId));
                              if (existsIdx >= 0) {
                                const copy = [...prev];
                                copy[existsIdx] = ratedObj;
                                return copy;
                              }
                              return [ratedObj, ...prev];
                            });
                          }

                          // También actualiza la lista de recomendaciones si el backend la devolvió
                          if (data && data.recommendations) setRecommendations(data.recommendations);
                          else {
                            // Elimina la película valorada de las recomendaciones localmente
                            if (meta && meta.movieId) setRecommendations(prev => prev.filter(p => Number(p.movieId) !== Number(meta.movieId)));
                          }
                        }} setError={setError} />
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
