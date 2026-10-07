import { useEffect, useState } from "react";

import { api, errorText } from "../api/client";
import type { Weather } from "../api/types";

export function WeatherCard() {
  const [weather, setWeather] = useState<Weather | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    api
      .get<Weather>("/api/integrations/weather")
      .then((response) => {
        setWeather(response.data);
        setState("ready");
      })
      .catch((error) => {
        setState("error");
        setMessage(errorText(error));
      });
  }, []);

  return (
    <aside className="weather">
      <h2>Погода для планирования</h2>
      {state === "loading" ? <p className="status">Запрашиваем Open-Meteo…</p> : null}
      {state === "error" ? <p className="error">Внешний сервис недоступен. {message}</p> : null}
      {state === "ready" && weather && !weather.available ? (
        <p className="empty">{weather.summary}. Доска продолжает работать без виджета.</p>
      ) : null}
      {state === "ready" && weather?.available ? (
        <p>
          {weather.location}: {weather.temperature_c}°C, {weather.summary}
          {weather.stale ? " (показан кэш)" : ""}
        </p>
      ) : null}
    </aside>
  );
}
