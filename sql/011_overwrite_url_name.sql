# Overwrite url_name for integrated genomes setting it to assembly.accession. 
# WARNING! This can create duplicates that need to be addressed by the accession-map script

# Clear existing url_names
UPDATE genome SET url_name = '';

# Set url_name to accession for current integrated genomes
WITH accession_map as (SELECT g.genome_id, a.accession
FROM genome g
JOIN assembly a ON g.assembly_id = a.assembly_id
JOIN genome_release gr ON g.genome_id = gr.genome_id
JOIN ensembl_release er ON gr.release_id = er.release_id
WHERE er.release_type = 'integrated' and er.is_current = 1 and g.suppressed = 0)
UPDATE genome SET url_name = accession_map.accession
FROM accession_map
WHERE genome.genome_id = accession_map.genome_id;