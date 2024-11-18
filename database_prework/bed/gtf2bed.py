import gzip
import pandas as pd
import re

# Input files
hgnc_file = "genes4bed.txt"
annotation_file = "/home/mani/SoftwareDevelopmentVIMMO/database_prework/bed/gencode.v47.basic.annotation.gtf.gz"  # Gzipped GTF file
output_bed_file = "genes_exons.bed"
unmatched_hgnc_file = "unmatched_hgnc_ids.txt"

# Load HGNC IDs into a set
with open(hgnc_file, "r") as f:
    hgnc_ids = set(line.strip() for line in f if line.strip())

# Parse GTF file to extract exons matching HGNC IDs
matched_hgnc_ids = set()
exon_data = []
with gzip.open(annotation_file, "rt") as f:  # Open gzipped GTF file
    for line in f:
        if line.startswith("#"):  # Skip headers
            continue
        cols = line.strip().split("\t")
        if cols[2] == "exon":  # Extract only exons
            chrom = cols[0]
            start = int(cols[3]) - 1  # Convert to 0-based start
            end = int(cols[4])
            info = cols[8]

            # Check for matching HGNC ID and extract gene symbol
            hgnc_id = None
            gene_name = None
            for field in info.split(";"):
                field = field.strip()
                if field.startswith("hgnc_id"):
                    hgnc_id = field.split('"')[1]
                if field.startswith("gene_name"):
                    gene_name = field.split('"')[1]

            # Filter based on HGNC ID
            if hgnc_id in hgnc_ids:
                matched_hgnc_ids.add(hgnc_id)
                exon_data.append((chrom, start, end, f"{gene_name}_exon", hgnc_id))

# Find unmatched HGNC IDs
unmatched_hgnc_ids = hgnc_ids - matched_hgnc_ids

# Save unmatched HGNC IDs to a file
with open(unmatched_hgnc_file, "w") as f:
    for hgnc_id in sorted(unmatched_hgnc_ids):
        f.write(hgnc_id + "\n")
print(f"Unmatched HGNC IDs written to {unmatched_hgnc_file}")

# Convert to DataFrame
df = pd.DataFrame(exon_data, columns=["chrom", "start", "end", "name", "hgnc_id"])

# Remove duplicates
df = df.drop_duplicates(subset=["chrom", "start", "end", "name", "hgnc_id"])

# Sort by chromosome order and position
def chromosome_sort_key(chrom):
    # Extract numbers or special identifiers (e.g., X, Y, MT) from chromosome
    match = re.match(r'chr(\d+|[XYMT]+)', chrom)
    if match:
        value = match.group(1)
        return (int(value) if value.isdigit() else float('inf'), value)
    return (float('inf'), chrom)  # Place unknown chromosomes at the end

df["chromosome_sort_key"] = df["chrom"].apply(chromosome_sort_key)
df = df.sort_values(by=["chromosome_sort_key", "start"]).drop(columns=["chromosome_sort_key"])

# Save to BED format
df.to_csv(output_bed_file, sep="\t", header=False, index=False)

print(f"Filtered BED file written to {output_bed_file}")