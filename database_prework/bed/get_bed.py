import pandas as pd
import requests
import time
from pathlib import Path
import gzip

def get_panel_exons(csv_file, padding=100, output_file="panel_exome_regions.bed"):
    """Fetch exon regions for panel genes with padding using gene symbols"""
    
    # Read CSV file
    df = pd.read_csv(csv_file)
    
    # Get unique gene symbols
    gene_symbols = df['Gene Symbol'].unique()
    print(f"Found {len(gene_symbols)} unique genes")
    
    # Ensembl API settings
    base_url = "https://rest.ensembl.org"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "python-requests/panel_exome_fetcher"
    }
    
    count = 0
    with open(output_file, 'w') as f:
        for symbol in gene_symbols:
            try:
                # First get the Ensembl ID for the gene symbol
                lookup_url = f"{base_url}/lookup/symbol/homo_sapiens/{symbol}"
                response = requests.get(lookup_url, headers=headers)
                
                if response.status_code != 200:
                    print(f"Error looking up gene symbol {symbol}: {response.status_code}")
                    continue
                
                gene_data = response.json()
                gene_id = gene_data['id']
                
                # Now get the detailed information including exons
                detail_url = f"{base_url}/lookup/id/{gene_id}?expand=1"
                response = requests.get(detail_url, headers=headers)
                
                if response.status_code != 200:
                    print(f"Error fetching details for {symbol}: {response.status_code}")
                    continue
                
                gene_data = response.json()
                
                # Get canonical transcript
                transcripts = gene_data.get('Transcript', [])
                if not transcripts:
                    print(f"No transcripts found for gene {symbol}")
                    continue
                    
                canonical = next((t for t in transcripts if t.get('is_canonical')), transcripts[0])
                
                # Process exons
                exons = canonical.get('Exon', [])
                if not exons:
                    print(f"No exons found for gene {symbol}")
                    continue
                
                print(f"Processing {symbol}: {len(exons)} exons")
                
                for i, exon in enumerate(exons, 1):
                    # Calculate padded coordinates
                    start = max(0, exon['start'] - padding)
                    end = exon['end'] + padding
                    
                    # Create BED line
                    bed_line = (
                        f"chr{gene_data['seq_region_name']}\t"  # chromosome
                        f"{start}\t"                            # start
                        f"{end}\t"                             # end
                        f"{symbol}_exon_{i}\t"                 # name
                        f"0\t"                                 # score
                        f"{'+' if gene_data['strand'] == 1 else '-'}\n"  # strand
                    )
                    
                    f.write(bed_line)
                    count += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing gene {symbol}: {str(e)}")
                continue
    
    print(f"\nCompleted! Wrote {count} exon regions to {output_file}")
    
    if count > 0:
        # Sort the BED file by chromosome and position
        print("Sorting BED file...")
        sorted_file = output_file.replace('.bed', '.sorted.bed')
        
        # Read lines and sort them
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        # Custom sort key function to handle chromosome names properly
        def sort_key(line):
            chrom, start, *_ = line.split('\t')
            # Remove 'chr' prefix and convert chromosome to integer if possible
            chrom = chrom[3:]
            try:
                chrom_num = int(chrom)
            except ValueError:
                chrom_num = float('inf') if chrom == 'Y' else float('inf')-1 if chrom == 'X' else float('inf')-2
            return (chrom_num, int(start))
        
        sorted_lines = sorted(lines, key=sort_key)
        
        # Write sorted lines
        with open(sorted_file, 'w') as f:
            f.writelines(sorted_lines)
        
        # Compress the file
        print("Compressing output...")
        with open(sorted_file, 'rb') as f_in:
            with gzip.open(sorted_file + '.gz', 'wb') as f_out:
                f_out.write(f_in.read())
        
        print(f"Files created:\n{output_file}\n{sorted_file}\n{sorted_file + '.gz'}")
    else:
        print("No exon regions were written to file!")

if __name__ == "__main__":
    # Use your CSV file
    get_panel_exons("genes.csv")