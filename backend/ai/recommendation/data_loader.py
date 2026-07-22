import os
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.supported_extensions = ['.csv', '.json', '.xlsx', '.xls', '.parquet', '.tsv', '.txt']

    def load_all_data(self) -> pd.DataFrame:
        """
        Scans the data directory and loads all supported datasets into a single pandas DataFrame.
        """
        if not os.path.exists(self.data_dir):
            logger.warning(f"Data directory {self.data_dir} does not exist. Creating it.")
            os.makedirs(self.data_dir, exist_ok=True)
            return pd.DataFrame()

        dataframes = []

        for root, _, files in os.walk(self.data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()

                if ext not in self.supported_extensions:
                    logger.info(f"Skipping unsupported file format: {file}")
                    continue

                logger.info(f"Loading dataset: {file_path}")
                try:
                    df = self._load_file(file_path, ext)
                    if not df.empty:
                        dataframes.append(df)
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")

        if not dataframes:
            logger.warning("No valid data found in training_data directory.")
            return pd.DataFrame()

        # Merge all dataframes. Some columns might be missing in some datasets, Pandas handles this with NaN
        merged_df = pd.concat(dataframes, ignore_index=True)
        logger.info(f"Successfully loaded {len(merged_df)} total records from {len(dataframes)} datasets.")
        return merged_df

    def _load_file(self, file_path: str, ext: str) -> pd.DataFrame:
        lower_path = file_path.lower()
        if lower_path.endswith('.csv.xls') or lower_path.endswith('.csv.xlsx') or ext in ['.csv', '.tsv']:
            sep = '\t' if ext == '.tsv' else ','
            try:
                return pd.read_csv(file_path, sep=sep, encoding='utf-8', on_bad_lines='skip')
            except Exception:
                return pd.read_csv(file_path, encoding='latin1', on_bad_lines='skip')

        elif ext in ['.xlsx', '.xls']:
            try:
                return pd.read_excel(file_path)
            except Exception as e:
                logger.warning(f"Failed to read {file_path} as Excel ({e}). Attempting read_csv fallback...")
                try:
                    return pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
                except Exception:
                    return pd.read_csv(file_path, encoding='latin1', on_bad_lines='skip')

        elif ext == '.parquet':
            return pd.read_parquet(file_path)
        elif ext == '.json':
            try:
                return pd.read_json(file_path)
            except ValueError:
                return pd.read_json(file_path, lines=True)
        elif ext == '.txt':
            try:
                return pd.read_csv(file_path, sep='\t', encoding='utf-8', on_bad_lines='skip')
            except Exception:
                return pd.DataFrame()
        return pd.DataFrame()

