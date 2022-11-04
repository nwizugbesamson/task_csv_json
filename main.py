## imports
import os
import re
import csv
import json
import hashlib
import shutil

if os.path.exists('./NFTS'):
    shutil.rmtree('./NFTS')


## constants
FORMAT = 'CHIP-0007'


def parse_attributes(attr: str, gender: str) -> list[dict[str, str]]:
    """generate trait_type, value key pair 

    Args:
        attr (str): column containing attribute string(format -> 'key:value ; key: value')
        gender (str): column containing gender attribute

    Returns:
        list[dict[str, str]]: parsed attributes
    """
    attributes = attr.strip().split(sep=';')
    parsed_attributes = [
        {
            'trait_type': attr.split(':')[0], 
            'value': attr.split(':')[1]  
            } for attr in attributes if ':' in attr
            ]
    parsed_attributes.append({
        'trait_type': 'gender',
        'value': gender
    })
    return parsed_attributes


def parse_files(team: str, row: dict, total: int) -> dict[str, str | list | dict]:
    """Parse data row into CHIP-0007 json format

    Args:
        team (str): NFT team
        row (dict): CSV row
        total (int): NFT total

    Returns:
        dict[str, str | list | dict]: parsed data
    """
    json_format = {}
    json_format['format'] = FORMAT
    json_format['name'] = row['Name']
    json_format['description'] = row['Description']
    json_format['minting_tool'] = team
    json_format['sensitive_content'] = False
    json_format['series_number'] = row['Series Number']
    json_format['series_total'] = total
    json_format['attributes'] = parse_attributes(row['attributes'], row['Gender'])
    json_format['collection'] = {
        'name': 'Zuri NFT Tickets for Free Lunch',
        'id': row['UUID'],
        'attributes': [
            {
                'type': 'description',
                'value': 'Rewards for accomplishments during HNGi9'
            }
        ]
    }
    json_format['data'] =  {
        "example_data": None
        }
    
    return json_format


def calculate_hash(file_path: str) -> str:
    """calculate Sha256 hash of json file

    Args:
        file_path (str): 

    Returns:
        str: Generated Sha256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def main(input):
    """Parse NFT data into JSON files 
       Save copy of file with Sha256 hash of Generated Json attached per row

    Args:
        input (_type_): file path of read csv
        output (_type_): file path of output csv

    """
    output = f'{input.split(".")[0]}.output.csv'
    with open(input, 'r') as read_obj, open(output, 'w') as write_obj:
        ## extract column names and NFT total
        team = None
        columns = read_obj.readline().split(',')
        total = read_obj.readlines()[-1].split(',')[1]
        columns.append('Sha256 hash')
        columns[7] = columns[7].replace('\n', '')

        ## instantiate reader and writer objects
        read_obj.seek(0)
        reader = csv.DictReader(read_obj)
        writer = csv.DictWriter(write_obj, fieldnames=columns)
        writer.writeheader()
        os.mkdir('./NFTS')

        ## loop through rows and parse data to json format
        for row in reader:
            ## extract team name and create directory for team
            if re.match(r'\w+', row['TEAM NAMES']):
                team = row['TEAM NAMES']
                os.mkdir(f'./NFTS/{team}')
            json_data = parse_files(team=team, row=row, total=total)
            file_name = f'./NFTS/{team}/{row["Filename"]}.json'
            with open(file_name, mode='w') as f:
                json.dump(json_data, f)
            hash = calculate_hash(file_name)
            row['Sha256 hash'] = hash
            writer.writerow(row)


if __name__ == '__main__':
    main(input("input csv filename: "))

