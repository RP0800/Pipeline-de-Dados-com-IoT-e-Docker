from pathlib import Path
import os
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "IOT-temp.csv"
VIEWS_PATH = BASE_DIR / "sql" / "views.sql"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "iotdb")
DB_USER = os.getenv("DB_USER", "iotuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "iotpass")

ENGINE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {path}. "
            "Baixe IOT-temp.csv e coloque-o em data/."
        )

    df = pd.read_csv(path)

    expected = {"id", "room_id/id", "noted_date", "temp", "out/in"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(
            f"Colunas ausentes no CSV: {sorted(missing)}. "
            f"Colunas encontradas: {list(df.columns)}"
        )

    df = df.rename(
        columns={
            "id": "reading_id",
            "room_id/id": "room_id",
            "noted_date": "noted_date",
            "temp": "temperature",
            "out/in": "location",
        }
    )

    df["noted_date"] = pd.to_datetime(
        df["noted_date"], format="%d-%m-%Y %H:%M", errors="coerce"
    )
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["location"] = df["location"].astype("string").str.strip()

    before = len(df)
    df = df.dropna(subset=["noted_date", "temperature", "location"]).copy()
    removed = before - len(df)

    print(f"Registros lidos: {before}")
    print(f"Registros válidos: {len(df)}")
    print(f"Registros descartados por campos inválidos: {removed}")

    return df


def main():
    df = load_csv(CSV_PATH)
    engine = create_engine(ENGINE_URL)

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE temperature_readings"))

    df.to_sql(
        "temperature_readings",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )

    views_sql = VIEWS_PATH.read_text(encoding="utf-8")
    statements = [s.strip() for s in views_sql.split(";") if s.strip()]

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))

        total = conn.execute(
            text("SELECT COUNT(*) FROM temperature_readings")
        ).scalar_one()

    print(f"Dados inseridos no PostgreSQL: {total}")
    print("Views SQL criadas/atualizadas com sucesso.")


if __name__ == "__main__":
    main()
