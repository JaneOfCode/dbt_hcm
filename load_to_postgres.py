import json
import psycopg2

### PostgreSQL parameters ###
DB_PARAMS = {
    "dbname": "hcm_db",
    "user": "jane",
    "password": "psw",
    "host": "localhost",
    "port": 5432
}

### Data taken from created API-based JSON file ###
with open("hcm_gene_data.json", "r", encoding="utf-8") as f:
    genes = json.load(f)

print(f"{len(genes)} JSON records found.")

### Main Upload ###
conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

for gene in genes:
    gene_symbol = gene.get("gene_symbol")
    confidence_level = int(gene["confidence_level"]) if str(gene["confidence_level"]).isdigit() else None
    mode_of_inheritance = gene.get("mode_of_inheritance")
    ensembl_id = gene.get("ensembl_id")
    chromosome = gene.get("chromosome")
    ncbi_description = gene.get("ncbi_description", "")

    if isinstance(gene.get("protein_name"), dict):
        protein_name = gene["protein_name"].get("value", "")
    else:
        protein_name = gene.get("protein_name", "")

    associated_diseases = gene.get("associated_diseases", [])

    uniprot_id = gene.get("uniprot_id")

    json_data = json.dumps(gene)

    cursor.execute(
        """
        INSERT INTO hcm_schema.raw_genes 
        (gene_symbol, confidence_level, mode_of_inheritance, 
         ensembl_id, chromosome, ncbi_description, 
         uniprot_id, protein_name, associated_diseases, json_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            gene_symbol,
            confidence_level,
            mode_of_inheritance,
            ensembl_id,
            chromosome,
            ncbi_description,
            uniprot_id,
            protein_name,
            associated_diseases,
            json_data
        )
    )

conn.commit()
cursor.close()
conn.close()

print("Data successfully loaded to PostgreSQL.")
