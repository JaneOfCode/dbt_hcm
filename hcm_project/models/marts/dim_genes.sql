{{ config(materialized='table') }}

SELECT
    gene_symbol,
    confidence_level,
    mode_of_inheritance,
    ensembl_id,
    chromosome,
    ncbi_description,
    uniprot_id,
    protein_name,
    associated_diseases
FROM {{ ref('stg_raw_genes') }}
