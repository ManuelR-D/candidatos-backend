"""
Script to generate SQL INSERT statements from JSON files in wayback_downloads directory.
Reads senator data from JSON files and creates INSERT statements for the database.
"""
import json
import os
from pathlib import Path
from datetime import datetime
import hashlib
import unicodedata


def clean_sql_value(value):
    """Clean and escape SQL values."""
    if value is None or value == "" or value == "Sin Datos":
        return "NULL"
    
    # Escape single quotes for SQL
    value_str = str(value).replace("'", "''")
    return f"'{value_str}'"


def parse_date(date_str):
    """Parse date string and return SQL-compatible format."""
    if not date_str or date_str == "Sin Datos" or date_str == "":
        return "NULL"
    
    try:
        # Expected format: YYYY-MM-DD
        datetime.strptime(date_str, "%Y-%m-%d")
        return f"'{date_str}'"
    except ValueError:
        return "NULL"


def normalize_text(value):
    """Normalize text by removing accents, trimming, and uppercasing."""
    if value is None or value == "" or value == "Sin Datos":
        return ""
    text = str(value)
    text = " ".join(text.split())
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.strip().upper()


def generate_representative_insert(row, json_filename, generated_id_counter):
    """Generate SQL INSERT statement for a representative."""
    # Extract data from JSON row
    last_name = clean_sql_value(row.get("APELLIDO"))
    first_name = clean_sql_value(row.get("NOMBRE"))
    province = clean_sql_value(row.get("PROVINCIA"))
    
    # Handle different field names for party (older vs newer files)
    party = clean_sql_value(row.get("PARTIDO") or row.get("PARTIDO O ALIANZA"))
    
    coalition = clean_sql_value(row.get("BLOQUE"))
    legal_start = parse_date(row.get("D_LEGAL"))
    legal_end = parse_date(row.get("C_LEGAL"))
    real_start = parse_date(row.get("D_REAL"))
    real_end = clean_sql_value(row.get("C_REAL"))
    email = clean_sql_value(row.get("EMAIL"))
    phone = clean_sql_value(row.get("TELEFONO"))
    facebook = clean_sql_value(row.get("FACEBOOK"))
    twitter = clean_sql_value(row.get("TWITTER"))
    instagram = clean_sql_value(row.get("INSTAGRAM"))
    youtube = clean_sql_value(row.get("YOUTUBE"))
    
    # Create full name
    if last_name != "NULL" and first_name != "NULL":
        full_name = f"'{row.get('APELLIDO')} {row.get('NOMBRE')}'"
    elif last_name != "NULL":
        full_name = last_name
    else:
        full_name = first_name
    
    # Determine external_id
    # 1. If "ID" field exists, use it
    # 2. Otherwise, generate sequential ID starting from 1000000
    if row.get("ID"):
        external_id = clean_sql_value(row.get("ID"))
        next_counter = generated_id_counter  # Don't increment
    else:
        external_id = clean_sql_value(str(generated_id_counter))
        next_counter = generated_id_counter + 1
    
    # Check if values are NULL (not the string 'NULL')
    province_is_null = province == "NULL"
    party_is_null = party == "NULL"
    coalition_is_null = coalition == "NULL"
    
    sql = f"""
-- Insert representative from {json_filename}
DO $$
DECLARE
    v_province_id INTEGER;
    v_party_id INTEGER;
    v_coalition_id INTEGER;
BEGIN
    -- Get or create Province
    {"-- Province is NULL, skipping" if province_is_null else f'''INSERT INTO Province (Name) VALUES ({province})
    ON CONFLICT DO NOTHING;
    SELECT UniqueID INTO v_province_id FROM Province WHERE Name = {province};'''}
    
    -- Get or create Party
    {"-- Party is NULL, skipping" if party_is_null else f'''INSERT INTO Party (Name) VALUES ({party})
    ON CONFLICT DO NOTHING;
    SELECT UniqueID INTO v_party_id FROM Party WHERE Name = {party};'''}
    
    -- Get or create Coalition
    {"-- Coalition is NULL, skipping" if coalition_is_null else f'''INSERT INTO Coalition (Name) VALUES ({coalition})
    ON CONFLICT (Name) DO NOTHING;
    SELECT UniqueID INTO v_coalition_id FROM Coalition WHERE Name = {coalition};'''}
    
    -- Insert Representative if not exists (only if we have required fields)
    {"-- Cannot insert: Province or Party is NULL" if province_is_null or party_is_null else f'''INSERT INTO Representative (
        External_id,
        Full_name,
        Last_name,
        First_name,
        Province_id,
        Party_id,
        Coalition_id,
        Legal_start_date,
        Legal_end_date,
        Real_start_date,
        Real_end_date,
        Email,
        Phone,
        Facebook_url,
        Twitter_url,
        Instagram_url,
        Youtube_url
    )
    SELECT
        {external_id},
        {full_name},
        {last_name},
        {first_name},
        v_province_id,
        v_party_id,
        v_coalition_id,
        {legal_start},
        {legal_end},
        {real_start},
        {real_end},
        {email},
        {phone},
        {facebook},
        {twitter},
        {instagram},
        {youtube}
    WHERE NOT EXISTS (
        SELECT 1 FROM Representative 
        WHERE Last_name = {last_name} 
        AND First_name = {first_name}
        AND Legal_start_date = {legal_start}
        AND Province_id = v_province_id
    );'''}
END $$;
"""
    return sql, next_counter


def process_json_files(input_dir, output_file):
    """Process all JSON files and generate SQL file."""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"Error: Directory {input_dir} does not exist")
        return
    
    # Get all JSON files
    json_files = sorted(input_path.glob("senadores_*.json"))
    
    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files")
    
    # Open output SQL file
    with open(output_file, 'w', encoding='utf-8') as sql_file:
        # Write header
        sql_file.write("-- Auto-generated SQL INSERT statements\n")
        sql_file.write(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        sql_file.write(f"-- Source: {input_dir}\n")
        sql_file.write("-- This file contains INSERT statements for representatives from wayback machine snapshots\n\n")
        sql_file.write("BEGIN;\n\n")
        
        total_records = 0
        skipped_duplicates = 0
        generated_id_counter = 1000000  # Starting ID for files without "ID" field
        seen_representatives = set()
        
        # Process each JSON file
        for json_file in json_files:
            print(f"Processing {json_file.name}...")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if data has expected structure
                if "table" not in data or "rows" not in data["table"]:
                    print(f"  Warning: Unexpected structure in {json_file.name}")
                    continue
                
                rows = data["table"]["rows"]
                print(f"  Found {len(rows)} representatives")
                
                # Write comment for this file
                sql_file.write(f"-- Data from {json_file.name}\n")
                sql_file.write(f"-- {len(rows)} representatives\n\n")
                
                # Generate INSERT for each row
                for row in rows:
                    last_name_raw = row.get("APELLIDO")
                    first_name_raw = row.get("NOMBRE")
                    province_raw = row.get("PROVINCIA")
                    legal_start_raw = row.get("D_LEGAL")

                    dedupe_key = (
                        normalize_text(last_name_raw),
                        normalize_text(first_name_raw),
                        normalize_text(province_raw),
                        normalize_text(legal_start_raw),
                    )

                    if dedupe_key in seen_representatives:
                        skipped_duplicates += 1
                        continue

                    seen_representatives.add(dedupe_key)

                    insert_sql, generated_id_counter = generate_representative_insert(row, json_file.name, generated_id_counter)
                    sql_file.write(insert_sql)
                    sql_file.write("\n")
                    total_records += 1
                
                sql_file.write("\n")
                
            except json.JSONDecodeError as e:
                print(f"  Error parsing {json_file.name}: {e}")
            except Exception as e:
                print(f"  Error processing {json_file.name}: {e}")
        
        sql_file.write("COMMIT;\n")
        
        print(f"\nCompleted!")
        print(f"Total records processed: {total_records}")
        print(f"Duplicates skipped (accent-insensitive): {skipped_duplicates}")
        print(f"Output file: {output_file}")


if __name__ == "__main__":
    # Configuration
    input_directory = "./src/bdd/wayback_downloads"
    output_sql_file = "./src/bdd/insert_representatives_wayback.sql"
    
    print("=" * 60)
    print("SQL INSERT Generator for Wayback Machine Data")
    print("=" * 60)
    print()
    
    process_json_files(input_directory, output_sql_file)
    
    print()
    print("=" * 60)
