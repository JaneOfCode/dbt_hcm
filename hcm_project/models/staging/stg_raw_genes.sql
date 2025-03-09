{{ config(materialized='view') }}

SELECT
    id,
    gene_symbol,
    CAST(confidence_level AS INTEGER) AS confidence_level,
    mode_of_inheritance,
    ensembl_id,
    chromosome,
    ncbi_description,
    uniprot_id,
    protein_name,
    associated_diseases
FROM {{ source('hcm_schema', 'raw_genes') }}