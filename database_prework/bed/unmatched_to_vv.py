import requests
from urllib.parse import quote

with open("unmatched_hgnc38_ids.txt", 'r') as f:
    next(f)

    for line in f:
        id=quote(line)
        url=f"https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2/{id}/mane_select/all/GRCh38?content-type=application%2Fjson"
        print(url)
        data=requests.get(url)
        print(data.json())
        break
        