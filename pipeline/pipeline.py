import argparse
import pandas as pd


def main(day: int):
    """Main pipeline logic for a given day."""
    print(f"Running pipeline for day {day}")

    # Dummy DataFrame (example data)
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

    print(df.head())

    # Save to parquet using the provided day
    output_file = f"output_day_{day}.parquet"
    df.to_parquet(output_file)

    print(f"Saved to {output_file}")


if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Simple pipeline that saves a parquet file for a given day."
    )

    # Define required argument
    parser.add_argument(
        "day", type=int, help="Day number to run the pipeline for (e.g. 1-31)"
    )

    # Parse arguments safely
    args = parser.parse_args()

    # Run main logic
    main(args.day)
