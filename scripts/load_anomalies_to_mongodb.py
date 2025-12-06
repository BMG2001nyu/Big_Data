"""Script to load anomaly data into MongoDB."""
from __future__ import annotations

import argparse
import pathlib

import pandas as pd

from src.database.mongodb import get_database


def load_anomalies_to_mongodb(parquet_path: str | pathlib.Path) -> None:
    """Load anomaly parquet file into MongoDB."""
    parquet_path = pathlib.Path(parquet_path)
    if not parquet_path.exists():
        print(f"Warning: Anomaly file not found: {parquet_path}")
        return
    
    print(f"Reading anomaly file: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    print(f"Loaded {len(df)} anomaly records")
    
    db = get_database()
    collection = db["anomalies"]
    
    # Clear existing data
    collection.delete_many({})
    
    # Convert DataFrame to list of dicts
    documents = df.to_dict(orient="records")
    
    # Insert documents
    if documents:
        collection.insert_many(documents)
        print(f"Inserted {len(documents)} documents into 'anomalies' collection")
        
        # Create indexes
        collection.create_index("from_hour")
        collection.create_index("borough")
        collection.create_index([("from_hour", -1)])
        print("Indexes created successfully")
    
    print("✅ Anomaly data loading completed!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Load anomaly data into MongoDB")
    parser.add_argument(
        "--parquet",
        type=str,
        default="data/anomalies/anomaly_events.parquet",
        help="Path to anomaly parquet file",
    )
    args = parser.parse_args()
    
    load_anomalies_to_mongodb(args.parquet)


if __name__ == "__main__":
    main()

