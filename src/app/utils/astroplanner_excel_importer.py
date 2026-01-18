import pandas as pd

from app.domain.model.celestial_object import CelestialObject, CelestialsList
from app.domain.services.observability_calculation_service import ObservabilityCalculationService

observability_calculation_service = ObservabilityCalculationService()


class AstroPlannerExcelImporter:

    def __init__(self, filename):
        self.filename = filename

    def import_data(self) -> CelestialsList:
        # Read the Excel file
        df = pd.read_excel(self.filename, engine='openpyxl')

        # Filter the columns we are interested in
        columns_of_interest = ['ID', 'Type', 'Mag', 'Size', 'Altitude']
        filtered_df = df[columns_of_interest]

        # Drop rows with missing data in the columns of interest
        filtered_df = filtered_df.dropna(subset=columns_of_interest)

        # Replace commas with periods for numeric columns and strip degrees from Altitude
        filtered_df['Mag'] = filtered_df['Mag'].astype(str).str.replace(',', '.')
        filtered_df['Altitude'] = filtered_df['Altitude'].astype(str).str.replace(',', '.').str.rstrip('°')

        # Convert string columns to numeric
        filtered_df['Mag'] = pd.to_numeric(filtered_df['Mag'], errors='coerce')
        filtered_df['Altitude'] = pd.to_numeric(filtered_df['Altitude'], errors='coerce')

        # Normalize data, e.g., converting sizes from arcseconds to arcminutes if necessary
        filtered_df['Size'] = filtered_df['Size'].astype(str).str.replace(',', '.').apply(self.normalize_size)

        # Calculate observability scores and store results
        celestial_objects_data: CelestialsList = []
        for _, row in filtered_df.iterrows():
            try:
                celestial_object: CelestialObject = self.read_row_as_celestial_object(row)
                print('read celestial object:', celestial_object)
                celestial_objects_data.append(celestial_object)
            except ValueError as e:
                # Handle the case where conversion to float fails
                print(f"Warning: Could not convert data for row: {row}. Error: {e}")
                continue

        return celestial_objects_data

    @staticmethod
    def read_row_as_celestial_object(row) -> CelestialObject:
        try:
            return CelestialObject(
                name=(row['ID']),
                object_type=(row['Type']),
                magnitude=(float(row['Mag'])),
                size=(float(row['Size'])),
                altitude=(float(row['Altitude']))
            )
        except ValueError as e:
            # If conversion fails, raise an error with a descriptive message
            raise ValueError(f"Error processing row {row['ID']}: {e}")

    @staticmethod
    def normalize_size(size_value):
        # Check if size_value is a string and contains arcminutes or arcseconds
        if isinstance(size_value, str):
            if "'" in size_value:
                # Convert from arcminutes to arcminutes (strip the ' and convert to float)
                return float(size_value.replace("'", ""))
            elif '"' in size_value:
                # Convert from arcseconds to arcminutes (strip the " and divide by 60)
                return float(size_value.replace('"', "")) / 60
        # If it's already a numeric value, return as is or you can adjust as needed
        return float(size_value)
