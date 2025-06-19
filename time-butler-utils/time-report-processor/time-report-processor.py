#!/usr/bin/env python3

"""
Time Report Processor
Appends weekly, monthly, or project time reports from CSV files to a main Excel file.

Usage:
   python time_report_processor.py <csv_file_path> [excel_file_path]

Example:
   python time_report_processor.py weekly_report.csv
   python time_report_processor.py monthly_report.csv main_reports.xlsx
   python time_report_processor.py SPA2-Generic_report.csv project_reports.xlsx
"""

import pandas as pd
import argparse
import sys
from pathlib import Path
from datetime import datetime
import logging
import re

# Configure logging
logging.basicConfig(
   level=logging.INFO,
   format='%(asctime)s - %(levelname)s - %(message)s',
   handlers=[
      logging.StreamHandler()
   ]
)

class TimeReportProcessor:
   """Handles processing and appending time reports to Excel files."""
   EXPECTED_COLUMNS = {
      'weekly': [
         'Week', 'Date', 'StartingTime', 'EndingTime', 'Hours', 'Description', 'Closed'
      ],
      'monthly': [
         'Month', 'Week', 'Date', 'StartingTime', 'EndingTime', 'Hours', 'Description', 'Closed'
      ],
      'project': [
         'hours', 'description', 'created', 'id'
      ]
   }

   def __init__(self, csv_file_path, excel_file_path=None):
      self.csv_file_path = Path(csv_file_path)
      self.excel_file_path = Path(excel_file_path or 'time_reports.xlsx')
      if not self.csv_file_path.exists():
         raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")

   def extract_project_name(self, filename):
      name = Path(filename).stem
      match = re.match(r'^([^_]+(?:-[^_]+)*)_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_time_report$', name)
      if match:
         return match.group(1)
      match = re.match(r'^([^_]+(?:-[^_]+)*)_time_report$', name)
      if match:
         return match.group(1)
      return name

   def detect_report_type(self, df):
      columns = [col.lower() for col in df.columns.tolist()]
      project_columns = ['hours', 'description', 'created', 'id']
      if all(col in columns for col in project_columns):
         project_name = self.extract_project_name(self.csv_file_path.name)
         return 'project', project_name
      if 'month' in columns:
         return 'monthly', None
      if 'week' in columns and 'month' not in columns:
         return 'weekly', None
      raise ValueError(
         f"Cannot determine report type. Expected columns for:\n"
         f"- Weekly: Week, Date, StartingTime, EndingTime, Hours, Description, Closed\n"
         f"- Monthly: Month, Week, Date, StartingTime, EndingTime, Hours, Description, Closed\n"
         f"- Project: hours, description, created, id\n"
         f"Found columns: {df.columns.tolist()}"
      )

   def validate_columns(self, df, report_type):
      expected_cols = self.EXPECTED_COLUMNS[report_type]
      actual_cols = df.columns.tolist()
      if report_type == 'project':
         missing_cols = [col for col in expected_cols if col not in actual_cols]
         if missing_cols:
            raise ValueError(f"Missing required columns for project report: {missing_cols}")
         return df[expected_cols].copy()
      col_mapping = {}
      for expected_col in expected_cols:
         found = False
         for actual_col in actual_cols:
            if expected_col.lower() == actual_col.lower():
               col_mapping[actual_col] = expected_col
               found = True
               break
         if not found:
            logging.warning(f"Expected column '{expected_col}' not found. Available: {actual_cols}")
      df_renamed = df.rename(columns=col_mapping)
      for col in expected_cols:
         if col not in df_renamed.columns:
            df_renamed[col] = pd.NA
            logging.warning(f"Added missing column '{col}' with NaN values")
      df_ordered = df_renamed[expected_cols].copy()
      return df_ordered

   def remove_timezone_from_datetime(self, dt_series):
      """Remove timezone information from datetime series to make it Excel-compatible."""
      if dt_series.dtype.name.startswith('datetime'):
         # Check if any datetime values have timezone info
         if hasattr(dt_series.dtype, 'tz') and dt_series.dtype.tz is not None:
            # Convert to timezone-naive by removing timezone info
            dt_series = dt_series.dt.tz_localize(None)
            logging.info("Removed timezone information from datetime column for Excel compatibility")
         elif dt_series.dt.tz is not None:
            # Alternative method for timezone-aware series
            dt_series = dt_series.dt.tz_localize(None)
            logging.info("Removed timezone information from datetime column for Excel compatibility")
      return dt_series

   def process_data(self, df, report_type):
      df_processed = df.copy()
      if report_type == 'project':
         if 'hours' in df_processed.columns:
            try:
               df_processed['hours'] = pd.to_numeric(df_processed['hours'], errors='coerce')
               logging.info("Successfully converted hours column to numeric")
            except Exception as e:
               logging.warning(f"Could not convert hours column to numeric: {e}")
         if 'id' in df_processed.columns:
            try:
               # Convert id to string to ensure consistent data type for merging
               df_processed['id'] = df_processed['id'].astype(str)
               logging.info("Successfully converted id column to string")
            except Exception as e:
               logging.warning(f"Could not convert id column to string: {e}")
         if 'created' in df_processed.columns:
            try:
               df_processed['created'] = pd.to_datetime(df_processed['created'], utc=True)
               # Remove timezone information for Excel compatibility
               df_processed['created'] = self.remove_timezone_from_datetime(df_processed['created'])
               logging.info("Successfully converted created column to datetime")
            except Exception as e:
               logging.warning(f"Could not convert created column to datetime: {e}")
      else:
         if 'Date' in df_processed.columns:
            try:
               df_processed['Date'] = pd.to_datetime(df_processed['Date'])
               # Remove timezone information for Excel compatibility
               df_processed['Date'] = self.remove_timezone_from_datetime(df_processed['Date'])
               logging.info("Successfully converted Date column to datetime")
            except Exception as e:
               logging.warning(f"Could not convert Date column to datetime: {e}")
         if 'Hours' in df_processed.columns:
            try:
               df_processed['Hours'] = pd.to_numeric(df_processed['Hours'], errors='coerce')
               logging.info("Successfully converted Hours column to numeric")
            except Exception as e:
               logging.warning(f"Could not convert Hours column to numeric: {e}")
         for col in ['Week', 'Month']:
            if col in df_processed.columns:
               try:
                  df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
                  logging.info(f"Successfully converted {col} column to numeric")
               except Exception as e:
                  logging.warning(f"Could not convert {col} column to numeric: {e}")
         if 'Closed' in df_processed.columns:
            try:
               df_processed['Closed'] = df_processed['Closed'].map({
                  'true': True, 'True': True, 'TRUE': True, True: True,
                  'false': False, 'False': False, 'FALSE': False, False: False
               })
               logging.info("Successfully converted Closed column to boolean")
            except Exception as e:
               logging.warning(f"Could not convert Closed column to boolean: {e}")
      return df_processed

   def load_csv(self):
      try:
         encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
         df = None
         for encoding in encodings:
            try:
               df = pd.read_csv(self.csv_file_path, encoding=encoding)
               logging.info(f"Successfully loaded CSV with {encoding} encoding")
               break
            except UnicodeDecodeError:
               continue
         if df is None:
            raise ValueError("Could not read CSV file with any supported encoding")
         if df.empty:
            raise ValueError("CSV file is empty")
         logging.info(f"Loaded CSV with {len(df)} rows and columns: {df.columns.tolist()}")
         report_type, project_name = self.detect_report_type(df)
         logging.info(f"Detected report type: {report_type}" + (f" (project: {project_name})" if project_name else ""))
         df_validated = self.validate_columns(df, report_type)
         df_processed = self.process_data(df_validated, report_type)
         return df_processed, report_type, project_name
      except Exception as e:
         logging.error(f"Error loading CSV file: {e}")
         raise

   def sanitize_sheet_name(self, name):
      if not name:
         name = "Project"
      invalid_chars = ['\\', '/', '?', '*', '[', ']', ':']
      for char in invalid_chars:
         name = name.replace(char, '_')
      if len(name) > 31:
         name = name[:31]
      return name

   def load_or_create_excel(self, project_name=None):
      excel_data = {}
      standard_sheets = {}
      if self.excel_file_path.exists():
         try:
            with pd.ExcelFile(self.excel_file_path) as xl:
               existing_sheets = xl.sheet_names
               logging.info(f"Found existing sheets: {existing_sheets}")
               for sheet_name in existing_sheets:
                  excel_data[sheet_name] = pd.read_excel(xl, sheet_name=sheet_name)
                  # Ensure existing data is also timezone-naive and has consistent data types
                  for col in excel_data[sheet_name].columns:
                     if excel_data[sheet_name][col].dtype.name.startswith('datetime'):
                        excel_data[sheet_name][col] = self.remove_timezone_from_datetime(excel_data[sheet_name][col])
                     # Ensure 'id' column is string type for project sheets
                     elif col == 'id':
                        excel_data[sheet_name][col] = excel_data[sheet_name][col].astype(str)
                  logging.info(f"Loaded existing sheet '{sheet_name}' with {len(excel_data[sheet_name])} rows")
               if project_name:
                  sanitized_name = self.sanitize_sheet_name(project_name)
                  if sanitized_name not in excel_data:
                     excel_data[sanitized_name] = pd.DataFrame(columns=self.EXPECTED_COLUMNS['project'])
                     logging.info(f"Created new project sheet '{sanitized_name}'")
         except Exception as e:
            logging.error(f"Error loading Excel file: {e}")
            excel_data = standard_sheets.copy()
            if project_name:
               sanitized_name = self.sanitize_sheet_name(project_name)
               excel_data[sanitized_name] = pd.DataFrame(columns=self.EXPECTED_COLUMNS['project'])
      else:
         excel_data = standard_sheets.copy()
         if project_name:
            sanitized_name = self.sanitize_sheet_name(project_name)
            excel_data[sanitized_name] = pd.DataFrame(columns=self.EXPECTED_COLUMNS['project'])
         logging.info("Created new Excel file structure")
      return excel_data

   def check_duplicates(self, new_data, existing_data, report_type, project_name=None):
    if existing_data.empty:
        return new_data
    if report_type == 'project':
        key_columns = ['id']
    else:
        key_columns = ['Date', 'StartingTime', 'EndingTime']
        if report_type == 'monthly':
            key_columns = ['Month', 'Week'] + key_columns
        else:
            key_columns = ['Week'] + key_columns
    available_key_columns = [col for col in key_columns if col in new_data.columns and col in existing_data.columns]
    if not available_key_columns:
        logging.warning("No common key columns found for duplicate detection")
        return new_data
    merged = new_data.merge(
        existing_data[available_key_columns],
        on=available_key_columns,
        how='left',
        indicator=True
    )
    duplicates_mask = merged['_merge'] == 'both'
    duplicates_count = duplicates_mask.sum()
    if duplicates_count > 0:
        logging.warning(f"Found {duplicates_count} duplicate entries - they will be discarded and not added")
        print(f"⚠️  {duplicates_count} duplicate entries found and discarded.")
    # Only keep rows that are not duplicates
    unique_new_data = new_data.loc[~duplicates_mask].reset_index(drop=True)
    return unique_new_data

   """def append_data(self, new_data, report_type, excel_data, project_name=None):
      if report_type == 'project':
         sheet_name = self.sanitize_sheet_name(project_name)
      else:
         sheet_name = report_type
      new_data_clean = self.check_duplicates(new_data, excel_data.get(sheet_name, pd.DataFrame()), report_type, project_name)
      new_data_clean = new_data_clean.copy()
      new_data_clean['Import_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      new_data_clean['Source_File'] = self.csv_file_path.name
      if sheet_name not in excel_data or excel_data[sheet_name].empty:
         excel_data[sheet_name] = new_data_clean
      else:
         excel_data[sheet_name] = pd.concat(
            [excel_data[sheet_name], new_data_clean],
            ignore_index=True
         )
      logging.info(f"Appended {len(new_data_clean)} rows to '{sheet_name}' sheet")
      return excel_data
"""
   def append_data(self, new_data, report_type, excel_data, project_name=None):
      # Determine year for weekly/monthly reports
      if report_type in ['weekly', 'monthly']:
         # Try to extract year from the 'Date' column
         if 'Date' in new_data.columns and not new_data['Date'].isnull().all():
            try:
               # Ensure 'Date' is datetime
               dates = pd.to_datetime(new_data['Date'], errors='coerce')
               year = dates.dt.year.mode()[0]  # Most common year in the data
            except Exception:
               year = datetime.now().year
         else:
            year = datetime.now().year
         sheet_name = f"{report_type}_{year}"
      elif report_type == 'project':
         sheet_name = self.sanitize_sheet_name(project_name)
      else:
         sheet_name = report_type

      # Ensure the sheet exists in excel_data
      new_data_clean = self.check_duplicates(
         new_data,
         excel_data.get(sheet_name, pd.DataFrame()),
         report_type,
         project_name
      )
      new_data_clean = new_data_clean.copy()
      new_data_clean['Import_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      new_data_clean['Source_File'] = self.csv_file_path.name
      if sheet_name not in excel_data or excel_data[sheet_name].empty:
         excel_data[sheet_name] = new_data_clean
      else:
         excel_data[sheet_name] = pd.concat(
            [excel_data[sheet_name], new_data_clean],
            ignore_index=True
         )

      # Sort the sheet by date after appending
      date_col = None
      if report_type == 'project' and 'created' in excel_data[sheet_name].columns:
         date_col = 'created'
      elif 'Date' in excel_data[sheet_name].columns:
         date_col = 'Date'

      if date_col:
         excel_data[sheet_name] = excel_data[sheet_name].sort_values(by=date_col).reset_index(drop=True)

      logging.info(f"Appended {len(new_data_clean)} rows to '{sheet_name}' sheet")
      return excel_data

   def load_or_create_excel(self, project_name=None):
      excel_data = {}
      # Don't pre-create 'weekly' or 'monthly' sheets, as they are now year-based
      standard_sheets = {}
      if self.excel_file_path.exists():
         try:
            with pd.ExcelFile(self.excel_file_path) as xl:
               existing_sheets = xl.sheet_names
               logging.info(f"Found existing sheets: {existing_sheets}")
               for sheet_name in existing_sheets:
                  excel_data[sheet_name] = pd.read_excel(xl, sheet_name=sheet_name)
                  # Ensure existing data is also timezone-naive and has consistent data types
                  for col in excel_data[sheet_name].columns:
                     if excel_data[sheet_name][col].dtype.name.startswith('datetime'):
                        excel_data[sheet_name][col] = self.remove_timezone_from_datetime(excel_data[sheet_name][col])
                     # Ensure 'id' column is string type for project sheets
                     elif col == 'id':
                        excel_data[sheet_name][col] = excel_data[sheet_name][col].astype(str)
                  if sheet_name not in ['weekly', 'monthly'] and project_name:
                     sanitized_name = self.sanitize_sheet_name(project_name)
                     if sanitized_name not in excel_data:
                        excel_data[sanitized_name] = pd.DataFrame(columns=self.EXPECTED_COLUMNS['project'])
                        logging.info(f"Created new project sheet '{sanitized_name}'")
         except Exception as e:
            logging.error(f"Error loading Excel file: {e}")
            excel_data = standard_sheets.copy()
            if project_name:
               sanitized_name = self.sanitize_sheet_name(project_name)
               excel_data[sanitized_name] = pd.DataFrame(columns=self.EXPECTED_COLUMNS['project'])
      else:
         excel_data = standard_sheets.copy()
         if project_name:
            sanitized_name = self.sanitize_sheet_name(project_name)
            excel_data[sanitized_name] = pd.DataFrame(columns=self.EXPECTED_COLUMNS['project'])
         logging.info("Created new Excel file structure")
      return excel_data

   def process(self):
      try:
         logging.info(f"Starting processing of {self.csv_file_path}")
         new_data, report_type, project_name = self.load_csv()
         excel_data = self.load_or_create_excel(project_name)
         excel_data = self.append_data(new_data, report_type, excel_data, project_name)
         # Determine target_sheet for summary/printing
         if report_type in ['weekly', 'monthly']:
            if 'Date' in new_data.columns and not new_data['Date'].isnull().all():
               try:
                     dates = pd.to_datetime(new_data['Date'], errors='coerce')
                     year = dates.dt.year.mode()[0]
               except Exception:
                     year = datetime.now().year
            else:
               year = datetime.now().year
            target_sheet = f"{report_type}_{year}"
         else:
            target_sheet = self.sanitize_sheet_name(project_name) if report_type == 'project' else report_type

         new_summary = self.generate_summary(new_data, report_type)
         total_summary = self.generate_summary(excel_data[target_sheet], report_type)
         print(f"\n✅ Processing completed successfully!")
         print(f"📊 Summary:")
         print(f"   • Processed: {self.csv_file_path.name} ({report_type} report)")

         if project_name:
            print(f"   • Project: {project_name}")
         print(f"   • Added: {len(new_data)} entries")

         if new_summary.get('total_hours'):
            print(f"   • Hours added: {new_summary['total_hours']:.2f}")
            print(f"   • Avg hours/entry: {new_summary['avg_hours_per_entry']:.2f}")

         if new_summary.get('date_range'):
            print(f"   • Date range: {new_summary['date_range']['start']} to {new_summary['date_range']['end']}")

         if new_summary.get('weeks'):
            print(f"   • Weeks: {new_summary['weeks']}")

         if new_summary.get('months'):
            print(f"   • Months: {new_summary['months']}")

         print(f"\n📈 Total Records in '{target_sheet}' sheet:")
         print(f"   • Records: {len(excel_data[target_sheet])}")

         if total_summary.get('total_hours'):
            print(f"   • Total hours: {total_summary['total_hours']:.2f}")

         print(f"\n📋 All Sheets:")
         for sheet_name, df in excel_data.items():
            if not df.empty:
               # Determine report_type for summary
               if sheet_name.startswith('weekly_'):
                     summary_type = 'weekly'
               elif sheet_name.startswith('monthly_'):
                     summary_type = 'monthly'
               elif sheet_name in ['weekly', 'monthly']:
                     summary_type = sheet_name
               else:
                     summary_type = 'project'
               sheet_summary = self.generate_summary(df, summary_type)
               hours = sheet_summary.get('total_hours', 0)
               print(f"   • {sheet_name}: {len(df)} records" + (f", {hours:.2f} hours" if hours > 0 else ""))
         print(f"   • Output file: {self.excel_file_path}")
      except Exception as e:
         logging.error(f"Processing failed: {e}")
         print(f"\n❌ Error: {e}")
         sys.exit(1)

   def generate_summary(self, data, report_type):
      summary = {}
      if data.empty:
         return summary
      summary['total_entries'] = len(data)
      hours_col = 'hours' if report_type == 'project' else 'Hours'
      if hours_col in data.columns:
         summary['total_hours'] = data[hours_col].sum()
         summary['avg_hours_per_entry'] = data[hours_col].mean()
         summary['max_hours_entry'] = data[hours_col].max()
         summary['min_hours_entry'] = data[hours_col].min()
      date_col = 'created' if report_type == 'project' else 'Date'
      if date_col in data.columns:
         try:
            date_series = pd.to_datetime(data[date_col])
            summary['date_range'] = {
               'start': date_series.min().strftime('%Y-%m-%d'),
               'end': date_series.max().strftime('%Y-%m-%d')
            }
         except:
            pass
      if report_type == 'monthly' and 'Month' in data.columns:
         summary['months'] = sorted(data['Month'].dropna().unique().tolist())
      if report_type in ['weekly', 'monthly'] and 'Week' in data.columns:
         summary['weeks'] = sorted(data['Week'].dropna().unique().tolist())
      return summary

   def save_excel(self, excel_data):
      try:
         # Final check to ensure all datetime columns are timezone-naive before saving
         for sheet_name, df in excel_data.items():
            if not df.empty:
               for col in df.columns:
                  if df[col].dtype.name.startswith('datetime'):
                     excel_data[sheet_name][col] = self.remove_timezone_from_datetime(df[col])

         with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
            for sheet_name, df in excel_data.items():
               if not df.empty:
                  df.to_excel(writer, sheet_name=sheet_name, index=False)
                  worksheet = writer.sheets[sheet_name]
                  for column in worksheet.columns:
                     max_length = 0
                     column_letter = column[0].column_letter
                     for cell in column:
                        try:
                           if len(str(cell.value)) > max_length:
                              max_length = len(str(cell.value))
                        except:
                           pass
                     adjusted_width = min(max_length + 2, 50)
                     worksheet.column_dimensions[column_letter].width = adjusted_width
         logging.info(f"Successfully saved data to {self.excel_file_path}")
      except Exception as e:
         logging.error(f"Error saving Excel file: {e}")
         raise

   def print_excel_summary(self):
      excel_data = self.load_or_create_excel()
      print(f"\n📋 All Sheets:")
      for sheet_name, df in excel_data.items():
         if not df.empty:
            # Determine report_type for summary
            if sheet_name.startswith('weekly_'):
               summary_type = 'weekly'
            elif sheet_name.startswith('monthly_'):
               summary_type = 'monthly'
            elif sheet_name in ['weekly', 'monthly']:
               summary_type = sheet_name
            else:
               summary_type = 'project'
            sheet_summary = self.generate_summary(df, summary_type)
            hours = sheet_summary.get('total_hours', 0)
            print(f"   • {sheet_name}: {len(df)} records" + (f", {hours:.2f} hours" if hours > 0 else ""))
      print(f"   • Output file: {self.excel_file_path}")

   def process(self):
      try:
         logging.info(f"Starting processing of {self.csv_file_path}")
         new_data, report_type, project_name = self.load_csv()
         excel_data = self.load_or_create_excel(project_name)
         excel_data = self.append_data(new_data, report_type, excel_data, project_name)
         self.save_excel(excel_data)

         if report_type in ['weekly', 'monthly']:
            if 'Date' in new_data.columns and not new_data['Date'].isnull().all():
               try:
                     dates = pd.to_datetime(new_data['Date'], errors='coerce')
                     year = dates.dt.year.mode()[0]
               except Exception:
                     year = datetime.now().year
            else:
               year = datetime.now().year
            target_sheet = f"{report_type}_{year}"
         else:
            target_sheet = self.sanitize_sheet_name(project_name) if report_type == 'project' else report_type
         new_summary = self.generate_summary(new_data, report_type)
         total_summary = self.generate_summary(excel_data[target_sheet], report_type)

         print(f"\n✅ Processing completed successfully!")
         print(f"📊 Summary:")
         print(f"   • Processed: {self.csv_file_path.name} ({report_type} report)")

         if project_name:
            print(f"   • Project: {project_name}")
         print(f"   • Added: {len(new_data)} entries")

         if new_summary.get('total_hours'):
            print(f"   • Hours added: {new_summary['total_hours']:.2f}")
            print(f"   • Avg hours/entry: {new_summary['avg_hours_per_entry']:.2f}")

         if new_summary.get('date_range'):
            print(f"   • Date range: {new_summary['date_range']['start']} to {new_summary['date_range']['end']}")

         if new_summary.get('weeks'):
            print(f"   • Weeks: {new_summary['weeks']}")

         if new_summary.get('months'):
            print(f"   • Months: {new_summary['months']}")

         print(f"\n📈 Total Records in '{target_sheet}' sheet:")
         print(f"   • Records: {len(excel_data[target_sheet])}")
         if total_summary.get('total_hours'):
            print(f"   • Total hours: {total_summary['total_hours']:.2f}")
         print(f"\n📋 All Sheets:")
         for sheet_name, df in excel_data.items():
            if not df.empty:
               # Determine report_type for summary
               if sheet_name.startswith('weekly_'):
                     summary_type = 'weekly'
               elif sheet_name.startswith('monthly_'):
                     summary_type = 'monthly'
               elif sheet_name in ['weekly', 'monthly']:
                     summary_type = sheet_name
               else:
                     summary_type = 'project'
               sheet_summary = self.generate_summary(df, summary_type)
               hours = sheet_summary.get('total_hours', 0)
               print(f"   • {sheet_name}: {len(df)} records" + (f", {hours:.2f} hours" if hours > 0 else ""))
         print(f"   • Output file: {self.excel_file_path}")
      except Exception as e:
         logging.error(f"Processing failed: {e}")
         print(f"\n❌ Error: {e}")
         sys.exit(1)


def main():
   parser = argparse.ArgumentParser(
      description='Append time reports from CSV files to a main Excel file',
      formatter_class=argparse.RawDescriptionHelpFormatter,
      epilog='''
Examples:
  python time_report_processor.py week24_report.csv
  python time_report_processor.py month5_report.csv main_reports.xlsx
  python time_report_processor.py SPA2-Generic_report.csv project_reports.xlsx
  python time_report_processor.py data/report.csv output/reports.xlsx
      '''
   )
   parser.add_argument(
      'csv_file',
      help='Path to the CSV file containing time report data'
   )
   parser.add_argument(
      'excel_file',
      nargs='?',
      default='time_reports_archive.xlsx',
      help='Path to the Excel file to append data to (default: time_reports.xlsx)'
   )
   parser.add_argument(
      '--version',
      action='version',
      version='Time Report Processor v3.0'
   )
   parser.add_argument(
   '--summary',
   action='store_true',
   default=False,
   help='Print a summary of the provided Excel file and exit'
)
   args = parser.parse_args()
   processor = TimeReportProcessor(args.csv_file, args.excel_file)

   if args.summary:
      processor.print_excel_summary()
   else:
      processor.process()

if __name__ == '__main__':
   main()
