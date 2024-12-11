import json
from datetime import datetime
import argparse

def read_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def parse_date(entry_date):
    return datetime.fromisoformat(entry_date)


def deduplicate_records(records : list, record_name : str) -> dict:
    '''
    This function dedup records based on record's email and id and return the deduplicated record list and change log as a output

    Parameters:
    records(list) : list of records to dedup

    Return:
    dict: consist of deduplicated list and the corresponding change log
    '''
    id_map, email_map = {}, {}
    deduplicated, change_log = [], []

    for record in records:
        record_id, record_email = record['_id'], record['email']
        exist_record = id_map.get(record_id) or email_map.get(record_email)

        if exist_record:
            existing_date = parse_date(exist_record['entryDate'])
            current_date = parse_date(record['entryDate'])

            if current_date >= existing_date:
                field_changes = {}
                for field in record:
                    if record[field] != exist_record[field]:
                        field_changes[field] = {
                            'value_from': exist_record[field],
                            'value_to': record[field]
                        }
        
                change_log.append({
                    'source_record': exist_record,
                    'output_record': record,   
                    'field_changes': field_changes
                })

                if exist_record in deduplicated:
                    deduplicated.remove(exist_record)

        id_map[record_id], email_map[record_email] = record, record
        deduplicated.append(record)

    return {
        'deduplicated_records' : {record_name: deduplicated},
        'change_log' : {record_name: change_log}
    }


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input', help="Input JSON file to be dedpulicated.")

    args = arg_parser.parse_args()
    
    input_records = read_file(args.input)
    for record_name in input_records:
        result = deduplicate_records(input_records[record_name],record_name)
        #Generate out put
        for key in result.keys():
            write_json_file(f"{record_name}_{key}.json", result[key])
    
