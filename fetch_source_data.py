import requests
import json
import time

### APIs to fetch genomic data from various databases ###

# PanelApp API - Hypertrophic Cardiomyopathy panel's link
PANELAPP_URL = "https://panelapp.genomicsengland.co.uk/api/v1/panels/49/genes/"

# Ensembl API
ENSEMBL_URL = "https://rest.ensembl.org/lookup/symbol/homo_sapiens/"

# NCBI Entrez API
NCBI_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&retmode=json&id="

# UniProt API
UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/search"


### Fetching Functions ###
def fetch_panelapp_genes():
    """Fetching list of genes from PanelApp API."""
    response = requests.get(PANELAPP_URL)
    if response.status_code == 200:
        data = response.json()
        genes = [
            {
                "gene_symbol": gene["gene_data"]["gene_symbol"],
                "confidence_level": gene["confidence_level"],
                "mode_of_inheritance": gene["mode_of_inheritance"]
            }
            for gene in data["results"]
        ]
        return genes
    else:
        print("Error for PanelApp:", response.status_code)
        return []


def fetch_ensembl_data(gene_symbol):
    """Fetching data from Ensembl API."""
    response = requests.get(f"{ENSEMBL_URL}{gene_symbol}?content-type=application/json")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error for Ensembl ({gene_symbol}):", response.status_code)
        return None


def fetch_ncbi_data(gene_id):
    """Fetching gene data from NCBI Entrez."""
    response = requests.get(f"{NCBI_URL}{gene_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error for NCBI ({gene_id}):", response.status_code)
        return None


def fetch_uniprot_data(gene_symbol):
    """Fetching protein data from UniProt API."""
    query = f"gene:{gene_symbol}+AND+%28organism_id:9606%29"
    response = requests.get(f"{UNIPROT_URL}?query={query}&format=json")
    
    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            protein = data["results"][0]
            return {
                "uniprot_id": protein["primaryAccession"],
                "protein_name": protein.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", ""),
                "associated_diseases": [kw["name"] for kw in protein.get("keywords", []) if "disease" in kw["name"].lower()]
            }
    else:
        print(f"Error for UniProt ({gene_symbol}):", response.status_code)
    return None


### Main Workflow ###
if __name__ == "__main__":

    panelapp_genes = fetch_panelapp_genes()

    for gene_nr, gene in enumerate(panelapp_genes):

        gene_symbol = gene["gene_symbol"]
        print(f"{gene_nr+1}. Analyzing gene {gene_symbol}...")

        ensembl_data = fetch_ensembl_data(gene_symbol)
        if ensembl_data:
            gene["ensembl_id"] = ensembl_data.get("id")
            gene["chromosome"] = ensembl_data.get("seq_region_name")

        if "ensembl_id" in gene:
            ncbi_data = fetch_ncbi_data(gene["ensembl_id"])
            if ncbi_data and "result" in ncbi_data:
                gene["ncbi_description"] = ncbi_data["result"].get(gene["ensembl_id"], {}).get("description", "")

        uniprot_data = fetch_uniprot_data(gene_symbol)
        if uniprot_data:
            gene.update(uniprot_data)

        print("Done")
        time.sleep(1)

    with open("hcm_gene_data.json", "w", encoding="utf-8") as f:
        json.dump(panelapp_genes, f, indent=4)
    
    print("Data saved to hcm_gene_data.json")
