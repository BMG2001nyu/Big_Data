"""Script to load CSV traffic data into MongoDB."""
from __future__ import annotations

import argparse
import pathlib
from datetime import datetime

import pandas as pd
from tqdm import tqdm

from src.database.mongodb import get_database


def parse_date(row: pd.Series) -> datetime:
    """Parse date from row components."""
    year = int(row["yr"])
    month = int(row["m"])
    day = int(row["d"])
    hour = int(row["hh"])
    minute = int(row["mm"])
    return datetime(year, month, day, hour, minute)


def transform_row(row: pd.Series) -> dict:
    """Transform CSV row to MongoDB document."""
    timestamp = parse_date(row)
    return {
        "requestid": str(row["requestid"]),
        "borough": row["boro"],
        "timestamp": timestamp,
        "year": int(row["yr"]),
        "month": int(row["m"]),
        "day": int(row["d"]),
        "hour": int(row["hh"]),
        "minute": int(row["mm"]),
        "volume": int(row["vol"]),
        "segmentid": str(row["segmentid"]),
        "geometry": row["wktgeom"],
        "street": row["street"],
        "from_street": row["fromst"],
        "to_street": row["tost"],
        "direction": row["direction"],
        "date": timestamp.date().isoformat(),
    }


def create_summary_documents(df: pd.DataFrame) -> list[dict]:
    """Create daily summary documents grouped by date and borough."""
    df["date"] = pd.to_datetime(df[["yr", "m", "d"]].apply(
        lambda x: f"{int(x['yr'])}-{int(x['m']):02d}-{int(x['d']):02d}", axis=1
    )).dt.date
    
    summary = (
        df.groupby(["date", "boro"])
        .agg({
            "vol": "sum",
            "requestid": "count",
        })
        .reset_index()
    )
    
    summary.columns = ["date", "borough", "vehicle_count", "record_count"]
    
    return [
        {
            "date": row["date"].isoformat(),
            "borough": row["borough"],
            "vehicle_count": int(row["vehicle_count"]),
            "record_count": int(row["record_count"]),
        }
        for _, row in summary.iterrows()
    ]


def load_csv_to_mongodb(csv_path: str | pathlib.Path, batch_size: int = 1000) -> None:
    """Load CSV file into MongoDB collections."""
    csv_path = pathlib.Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    print(f"Reading CSV file: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from CSV")
    
    db = get_database()
    
    # Load raw data
    raw_collection = db["traffic_raw"]
    print(f"\nLoading raw data into 'traffic_raw' collection...")
    
    # Clear existing data if needed
    raw_collection.delete_many({})
    
    documents = []
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        doc = transform_row(row)
        documents.append(doc)
        
        if len(documents) >= batch_size:
            raw_collection.insert_many(documents)
            documents = []
    
    # Insert remaining documents
    if documents:
        raw_collection.insert_many(documents)
    
    print(f"Inserted {raw_collection.count_documents({})} documents into 'traffic_raw'")
    
    # Create indexes for better query performance
    print("\nCreating indexes...")
    raw_collection.create_index("timestamp")
    raw_collection.create_index("borough")
    raw_collection.create_index("date")
    raw_collection.create_index([("date", 1), ("borough", 1)])
    print("Indexes created successfully")
    
    # Create summary collection
    summary_collection = db["traffic_summary"]
    print(f"\nCreating summary data in 'traffic_summary' collection...")
    summary_collection.delete_many({})
    
    summary_docs = create_summary_documents(df)
    if summary_docs:
        summary_collection.insert_many(summary_docs)
        summary_collection.create_index("date")
        summary_collection.create_index("borough")
        summary_collection.create_index([("date", 1), ("borough", 1)])
        print(f"Inserted {len(summary_docs)} summary documents")
    
    print("\n✅ Data loading completed successfully!")
    print(f"Database: {db.name}")
    print(f"Collections created: traffic_raw, traffic_summary")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Load CSV traffic data into MongoDB")
    parser.add_argument(
        "--csv",
        type=str,
        default="data/raw/7ym2-wayt.csv",
        help="Path to CSV file",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for inserting documents",
    )
    args = parser.parse_args()
    
    load_csv_to_mongodb(args.csv, args.batch_size)


if __name__ == "__main__":
    main()

