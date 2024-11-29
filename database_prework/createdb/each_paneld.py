import requests
import json
import csv
items=[]
with open('../createdb/latest_panel_versions.csv', 'r') as pf:
    next(pf)
    for line in pf:
        cleaned_line = line.strip()
        cleaned_line=cleaned_line.split(",")
        items.append(cleaned_line)


with open('genes.csv', 'a', newline='') as csvfile:
    fieldnames = [
        'Panel ID', 'Gene ID', 'HGNC symbol', 'HGNC ID', 'Gene Symbol',
        'GRCh38 Chr', 'GRCh38 start', 'GRCh38 stop',
        'GRCh37 Chr', 'GRCh37 start', 'GRCh37 stop', 'Confidence'
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i in items:
        id = i[0]
        ver = i[-1]
        url = f'https://panelapp.genomicsengland.co.uk/api/v1/panels/{id}/?format=json&version={ver}'
        data = requests.get(url)
        json_data = data.json()

        panel_id = json_data.get('id', '')  # Get the panel ID from the JSON data

        # Iterate over each gene in the JSON data
        for gene_entry in json_data.get('genes', []):
            gene_data = gene_entry.get('gene_data', None)

            if gene_data:
                # Extract HGNC ID and symbols
                hgnc_id = gene_data.get('hgnc_id', '')
                hgnc_symbol = gene_data.get('hgnc_symbol', '')
                gene_symbol = gene_data.get('gene_symbol', '')

                # Extract Ensembl gene data for GRCh38 and GRCh37
                ensembl_genes = gene_data.get('ensembl_genes', {})
                grch38_data = ensembl_genes.get('GRch38', {})
                grch37_data = ensembl_genes.get('GRch37', {})

                # Function to extract the latest version data
                def get_latest_version_data(version_data):
                    if version_data:
                        latest_version = max(version_data.keys())
                        return version_data[latest_version]
                    return {}

                # Get the latest version data for GRCh38 and GRCh37
                grch38_info = get_latest_version_data(grch38_data)
                grch37_info = get_latest_version_data(grch37_data)

                # Function to parse chromosome location
                def parse_location(location):
                    if location:
                        chr_part, positions = location.split(':')
                        start_pos, end_pos = positions.split('-')
                        return chr_part, start_pos, end_pos
                    return '', '', ''

                # Extract GRCh38 location details
                grch38_chr, grch38_start, grch38_stop = parse_location(grch38_info.get('location', ''))

                # Extract GRCh37 location details
                grch37_chr, grch37_start, grch37_stop = parse_location(grch37_info.get('location', ''))

                # Use Ensembl ID as the Gene ID
                gene_id = grch38_info.get('ensembl_id') or grch37_info.get('ensembl_id', '')
                confidence = gene_entry.get('confidence_level', {})

                # Write the extracted data to the CSV file
                writer.writerow({
                    'Panel ID': panel_id,
                    'Gene ID': gene_id,
                    'HGNC symbol': hgnc_symbol,
                    'HGNC ID': hgnc_id,
                    'Gene Symbol': gene_symbol,
                    'GRCh38 Chr': grch38_chr,
                    'GRCh38 start': grch38_start,
                    'GRCh38 stop': grch38_stop,
                    'GRCh37 Chr': grch37_chr,
                    'GRCh37 start': grch37_start,
                    'GRCh37 stop': grch37_stop,
                    'Confidence' : confidence
                })
