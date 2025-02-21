import pandas as pd
from datetime import datetime
import json
import re
from typing import Union, List, Dict, Tuple

class InventoryControlSystem:
    def __init__(self):
        self.required_fields = ['product_id', 'product_type', 'expiration_date', 'stock_level']
        self.validation_errors = []
        self.reorder_threshold = 10

    def validate_date_format(self, date_str: str) -> bool:
        """Validate if date string matches YYYY-MM-DD format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def load_data(self, data: Union[str, Dict]) -> pd.DataFrame:
        """Load data from CSV or JSON string/dictionary"""
        try:
            if isinstance(data, str):
                if data.strip().startswith('{'):
                    # JSON data
                    json_data = json.loads(data)
                    df = pd.DataFrame(json_data['inventory'])
                else:
                    # CSV data
                    df = pd.read_csv(data)
            else:
                # Dictionary data
                df = pd.DataFrame(data['inventory'])
            return df
        except Exception as e:
            raise ValueError("ERROR: Invalid data format. Please provide data in CSV or JSON format.")

    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validate the data according to specified rules"""
        self.validation_errors = []
        
        # Check required fields
        missing_fields = set(self.required_fields) - set(df.columns)
        if missing_fields:
            self.validation_errors.append(f"ERROR: Missing required field(s): {', '.join(missing_fields)}")
            return False

        # Validate each record
        for idx, row in df.iterrows():
            # Validate stock_level
            try:
                stock_level = int(row['stock_level'])
                if stock_level < 0:
                    self.validation_errors.append(
                        f"ERROR: Invalid value for field(s): stock_level at row {idx + 1}. Stock level must be non-negative."
                    )
            except ValueError:
                self.validation_errors.append(
                    f"ERROR: Invalid data type for field(s): stock_level at row {idx + 1}. Must be an integer."
                )

            # Validate expiration_date
            if not self.validate_date_format(str(row['expiration_date'])):
                self.validation_errors.append(
                    f"ERROR: Invalid date format for field(s): expiration_date at row {idx + 1}. Must be YYYY-MM-DD."
                )

        return len(self.validation_errors) == 0

    def process_inventory(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Process inventory data and generate report"""
        # Sort data
        df_sorted = df.sort_values(['product_type', 'expiration_date'])
        
        # Add reorder flag
        df_sorted['reorder_flag'] = df_sorted['stock_level'].apply(
            lambda x: 'Reorder' if x < self.reorder_threshold else 'OK'
        )

        # Generate report statistics
        stats = {
            'total_records': len(df),
            'unique_product_types': df['product_type'].nunique(),
            'items_to_reorder': len(df[df['stock_level'] < self.reorder_threshold]),
            'average_stock_level': df['stock_level'].mean()
        }

        return df_sorted, stats

    def generate_report(self, data: Union[str, Dict]) -> str:
        """Generate full markdown report"""
        try:
            # Load and validate data
            df = self.load_data(data)
            is_valid = self.validate_data(df)
            
            if not is_valid:
                return "\n".join(self.validation_errors)

            # Process data
            processed_df, stats = self.process_inventory(df)

            # Generate markdown report
            report = []
            
            # Data Validation Report
            report.append("# Data Validation Report")
            report.append(f"- **Data Structure Check:** {stats['total_records']} records processed")
            report.append("- **Required Fields Check:** All required fields present")
            report.append("- **Data Type Validation:** All data types valid")
            report.append("- **Validation Summary:** Data validation successful")
            report.append("")

            # Sorting and Flagging Report
            report.append("# Sorting and Flagging Report")
            report.append("- **Sorting Process:**")
            report.append("  1. Records sorted by product_type (alphabetically)")
            report.append("  2. Within each product_type, sorted by expiration_date (ascending)")
            report.append("")
            report.append("- **Reorder Flag Determination:**")
            report.append(f"  - Reorder Threshold: {self.reorder_threshold} units")
            report.append("  - Logic Applied:")
            report.append("    ```")
            report.append("    IF stock_level < 10:")
            report.append("        reorder_flag = 'Reorder'")
            report.append("    ELSE:")
            report.append("        reorder_flag = 'OK'")
            report.append("    ```")
            report.append("")

            # Statistics
            report.append("# Inventory Statistics")
            report.append(f"- Total unique product types: {stats['unique_product_types']}")
            report.append(f"- Items flagged for reorder: {stats['items_to_reorder']}")
            report.append(f"- Average stock level: {stats['average_stock_level']:.2f}")
            report.append("")

            # Final Inventory Table
            report.append("# Final Inventory Table")
            report.append(processed_df.to_markdown(index=False))
            report.append("")

            # Feedback Request
            report.append("# Feedback Request")
            report.append("Would you like detailed calculations for any specific product? Rate this analysis (1-5).")

            return "\n".join(report)

        except Exception as e:
            return f"ERROR: An error occurred while processing the inventory data: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Example data
    example_data = {
    "inventory": [
    {"product_id": "E1111", "product_type": "Electronics", "expiration_date": "2024-06-01", "stock_level": 14},
    {"product_id": "F2222", "product_type": "Books", "expiration_date": "2023-12-10", "stock_level": 22},
    {"product_id": "G3333", "product_type": "Clothing", "expiration_date": "2024-02-15", "stock_level": 8},
    {"product_id": "H4444", "product_type": "Toys", "expiration_date": "2023-11-05", "stock_level": 5},
    {"product_id": "I5555", "product_type": "Home", "expiration_date": "2025-07-30", "stock_level": 19},
    {"product_id": "J6666", "product_type": "Garden", "expiration_date": "2024-08-25", "stock_level": 21},
    {"product_id": "K7777", "product_type": "Office", "expiration_date": "2023-10-20", "stock_level": 10},
    {"product_id": "L8888", "product_type": "Automotive", "expiration_date": "2024-03-10", "stock_level": 9},
    {"product_id": "M9999", "product_type": "Sports", "expiration_date": "2024-12-05", "stock_level": 7},
    {"product_id": "N1010", "product_type": "Health", "expiration_date": "2023-09-15", "stock_level": 18},
    {"product_id": "O1111", "product_type": "Beauty", "expiration_date": "2024-07-15", "stock_level": 12},
    {"product_id": "P1212", "product_type": "Electronics", "expiration_date": "2023-08-30", "stock_level": 16},
    {"product_id": "Q1313", "product_type": "Books", "expiration_date": "2024-09-10", "stock_level": 13},
    {"product_id": "R1414", "product_type": "Clothing", "expiration_date": "2024-03-25", "stock_level": 6},
    {"product_id": "S1515", "product_type": "Toys", "expiration_date": "2025-02-20", "stock_level": 20}
    ]
    }



    # Create instance and generate report
    inventory_system = InventoryControlSystem()
    report = inventory_system.generate_report(example_data)
    print(report)