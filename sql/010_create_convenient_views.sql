# View DDLs for convenience
CREATE OR REPLACE VIEW v_suppressed_genomes AS
SELECT 
    g.genome_uuid,
    og.name as 'organism_group',
    g.production_name,
    g.genebuild_date,
    g.suppression_details
FROM genome g 
JOIN organism o USING(organism_id) 
JOIN organism_group_member ogm USING(organism_id)
JOIN organism_group og USING(organism_group_id)
WHERE suppressed = 1; 

CREATE OR REPLACE VIEW v_genome_by_release AS
SELECT 
    g.genome_uuid,
    g.production_name,
    a.accession,
    g.genebuild_date,
    gr.is_current,
    er.name as 'ensembl_release',
    er.release_type 
FROM genome g 
JOIN genome_release gr USING(genome_id)
JOIN ensembl_release er USING(release_id)
JOIN assembly a USING(assembly_id);

CREATE OR REPLACE VIEW v_genome_release_info AS
SELECT
    g.genome_id,
    g.genome_uuid,
    g.production_name,
    er.name AS ens_release_name,
    last_part.name AS partial_release_name,
    last_part.version AS partial_release_version,
    dd.name AS dataset_name,
    ds.location AS db_host,
    ds.name AS core_db_name,
FROM genome g
JOIN (
    SELECT genome_id, name, version
    FROM (
        SELECT
            ggr.genome_id,
            eer.name,
            eer.version,
            ROW_NUMBER() OVER (
                PARTITION BY ggr.genome_id
                ORDER BY eer.version DESC
            ) AS rn
        FROM genome_release ggr
        JOIN ensembl_release eer USING (release_id)
        WHERE eer.release_type = 'partial'
    ) ranked
    WHERE rn = 1
) AS last_part USING (genome_id)
JOIN genome_release gr USING (genome_id)
JOIN genome_dataset gd
    ON g.genome_id = gd.genome_id
    AND gr.release_id = gd.release_id
JOIN ensembl_release er
    ON er.release_id = gr.release_id
JOIN dataset dd USING (dataset_id)
JOIN dataset_source ds USING (dataset_source_id)
WHERE
    dd.dataset_type_id = 2
    AND gr.is_current = 1
    AND er.release_type = 'integrated';
