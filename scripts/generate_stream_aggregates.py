"""Generate stream aggregates from MongoDB raw data."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta

from src.database.mongodb import get_database


def generate_stream_aggregates(window_hours: int = 1, limit: int = 100) -> None:
    """Generate time-windowed aggregates from raw traffic data."""
    db = get_database()
    raw_collection = db["traffic_raw"]
    aggregates_collection = db["stream_aggregates"]
    
    print(f"Generating stream aggregates with {window_hours}-hour windows...")
    
    # Clear existing aggregates
    aggregates_collection.delete_many({})
    
    # Get date range from raw data
    pipeline = [
        {
            "$group": {
                "_id": None,
                "min_date": {"$min": "$timestamp"},
                "max_date": {"$max": "$timestamp"},
            }
        }
    ]
    
    result = list(raw_collection.aggregate(pipeline))
    if not result:
        print("No data found in traffic_raw collection")
        return
    
    min_date = result[0]["min_date"]
    max_date = result[0]["max_date"]
    
    print(f"Data range: {min_date} to {max_date}")
    
    # Generate aggregates for each time window
    current_start = min_date.replace(minute=0, second=0, microsecond=0)
    window_delta = timedelta(hours=window_hours)
    aggregates = []
    
    while current_start < max_date:
        window_end = current_start + window_delta
        
        # Aggregate data for this window
        pipeline = [
            {
                "$match": {
                    "timestamp": {
                        "$gte": current_start,
                        "$lt": window_end,
                    }
                }
            },
            {
                "$group": {
                    "_id": "$borough",
                    "avg_vehicle_count": {"$avg": "$volume"},
                    "total_volume": {"$sum": "$volume"},
                    "record_count": {"$sum": 1},
                    "street": {"$first": "$street"},
                }
            }
        ]
        
        results = list(raw_collection.aggregate(pipeline))
        
        for result in results:
            aggregates.append({
                "window_start": current_start.isoformat(),
                "window_end": window_end.isoformat(),
                "borough": result["_id"],
                "roadwayname": result.get("street", ""),
                "avg_vehicle_count": float(result["avg_vehicle_count"]),
                "total_volume": int(result["total_volume"]),
                "record_count": int(result["record_count"]),
            })
        
        current_start = window_end
        
        if len(aggregates) >= limit:
            break
    
    # Insert aggregates
    if aggregates:
        aggregates_collection.insert_many(aggregates)
        print(f"Inserted {len(aggregates)} aggregate documents")
        
        # Create indexes
        aggregates_collection.create_index("window_end")
        aggregates_collection.create_index("borough")
        aggregates_collection.create_index([("window_end", -1)])
        print("Indexes created successfully")
    
    print("✅ Stream aggregates generation completed!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate stream aggregates from MongoDB")
    parser.add_argument(
        "--window-hours",
        type=int,
        default=1,
        help="Time window size in hours",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of aggregates to generate",
    )
    args = parser.parse_args()
    
    generate_stream_aggregates(args.window_hours, args.limit)


if __name__ == "__main__":
    main()

