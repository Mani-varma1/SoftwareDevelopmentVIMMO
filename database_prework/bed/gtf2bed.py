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

# Parse GTF file to extract prioritized exons matching HGNC IDs
priority_transcripts = {}
exon_data = []

with gzip.open(annotation_file, "rt") as f:  # Open gzipped GTF file
    for line in f:
        if line.startswith("#"):  # Skip headers
            continue
        cols = line.strip().split("\t")
        if cols[2] in ["transcript", "exon"]:  # Process transcripts and exons
            chrom = cols[0]
            start = int(cols[3]) - 1  # Convert to 0-based start
            end = int(cols[4])
            strand = cols[6]
            info = cols[8]

            # Extract relevant tags and fields
            hgnc_id = None
            gene_name = None
            transcript_id = None
            exon_number = None
            is_mane_select = "tag \"MANE_Select\"" in info
            is_mane_plus_clinical = "tag \"MANE_Plus_Clinical\"" in info
            is_canonical = "tag \"Ensembl_canonical\"" in info

            for field in info.split(";"):
                field = field.strip()
                if field.startswith("hgnc_id"):
                    hgnc_id = field.split('"')[1]
                elif field.startswith("gene_name"):
                    gene_name = field.split('"')[1]
                elif field.startswith("transcript_id"):
                    transcript_id = field.split('"')[1]
                elif field.startswith("exon_number"):
                    exon_number = field.split()[1]  # Exon number is numeric, no quotes

            # Skip if HGNC ID is not in the gene list
            if hgnc_id not in hgnc_ids:
                continue

            # Handle transcripts: prioritize MANE Select > MANE Plus Clinical > Canonical
            if cols[2] == "transcript":
                if hgnc_id not in priority_transcripts:
                    priority_transcripts[hgnc_id] = {"MANE_Select": None, "MANE_Plus_Clinical": None, "Ensembl_canonical": None}

                if is_mane_select:
                    priority_transcripts[hgnc_id]["MANE_Select"] = transcript_id
                elif is_mane_plus_clinical:
                    priority_transcripts[hgnc_id]["MANE_Plus_Clinical"] = transcript_id
                elif is_canonical:
                    priority_transcripts[hgnc_id]["Ensembl_canonical"] = transcript_id

            # Handle exons
            if cols[2] == "exon":
                exon_name = f"{gene_name}_exon{exon_number}" if exon_number else f"{gene_name}_exon"
                exon_data.append((chrom, start, end, exon_name, hgnc_id, strand, transcript_id))

# Filter exons based on prioritized transcripts
filtered_exon_data = []
matched_hgnc_ids = set()  # Now only add to this set if the gene has a valid transcript
for hgnc_id, transcripts in priority_transcripts.items():
    selected_transcript = (
        transcripts["MANE_Select"] or transcripts["MANE_Plus_Clinical"] or transcripts["Ensembl_canonical"]
    )
    if selected_transcript:  # Only include if a prioritized transcript is available
        matched_hgnc_ids.add(hgnc_id)  # Add only if the gene has a valid transcript
        for exon in exon_data:
            if exon[4] == hgnc_id and exon[6] == selected_transcript:  # Match on hgnc_id and transcript_id
                filtered_exon_data.append(exon[:6])  # Exclude transcript_id from the output

# Find unmatched HGNC IDs
unmatched_hgnc_ids = hgnc_ids - matched_hgnc_ids

# Save unmatched HGNC IDs to a file
with open(unmatched_hgnc_file, "w") as f:
    for hgnc_id in sorted(unmatched_hgnc_ids):
        f.write(hgnc_id + "\n")
print(f"Unmatched HGNC IDs written to {unmatched_hgnc_file}")

# Convert to DataFrame
df = pd.DataFrame(filtered_exon_data, columns=["chrom", "start", "end", "name", "hgnc_id", "strand"])

# Remove duplicates
df = df.drop_duplicates(subset=["chrom", "start", "end", "name", "hgnc_id", "strand"])

# Sort by chromosome order and position
def chromosome_sort_key(chrom):
    match = re.match(r'chr(\d+|[XYMT]+)', chrom)
    if match:
        value = match.group(1)
        return (int(value) if value.isdigit() else float('inf'), value)
    return (float('inf'), chrom)  # Place unknown chromosomes at the end

df["chromosome_sort_key"] = df["chrom"].apply(chromosome_sort_key)
df = df.sort_values(by=["chromosome_sort_key", "start"]).drop(columns=["chromosome_sort_key"])

# Reorder columns to match desired output
df = df[["chrom", "start", "end", "name", "hgnc_id", "strand"]]

# Save to BED format
df.to_csv(output_bed_file, sep="\t", header=False, index=False)

print(f"Filtered BED file written to {output_bed_file}")