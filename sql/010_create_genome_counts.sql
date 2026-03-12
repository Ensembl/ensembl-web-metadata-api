# Create a table with all species, copying out of genome / organism
drop table if exists taxonomy_counts;
create table taxonomy_counts as from (
  with valid_releases as (select * from ensembl_release where ((release_type =
        'integrated' and is_current = true) or (release_type = 'partial' and
        status = 'Released' and release_date >= (select release_date from
          ensembl_release where release_type = 'integrated' and is_current =
          true)))) select g.genome_id, g.organism_id, g.production_name,
  o.taxonomy_id from genome g inner join genome_release gr on gr.genome_id =
  g.genome_id inner join valid_releases vr on vr.release_id = gr.release_id inner
  join organism o on o.organism_id = g.organism_id where g.suppressed = false and
  gr.is_current = true group by all
);
alter table taxonomy_counts add column domain_tax_id int;
alter table taxonomy_counts add column release_id int;
update taxonomy_counts set release_id = 0;

insert into taxonomy_counts (release_id, genome_id, organism_id, production_name, taxonomy_id) select er.release_id, g.genome_id, g.organism_id, g.production_name,
    o.taxonomy_id from genome g inner join genome_release gr on gr.genome_id =
    g.genome_id inner join ensembl_release er on er.release_id = gr.release_id inner
    join organism o on o.organism_id = g.organism_id where g.suppressed = false and
    gr.is_current = true and er.status = 'Released';

# If there is newer data from NCBI, update our taxonomy_ids
update taxonomy_counts set taxonomy_id = new_tax_id from (select ntn.taxon_id as new_tax_id, genome_id from taxonomy_counts tc
      join ncbi_taxa_name ntn on cast(tc.taxonomy_id as text) = ntn.name and ntn.name_class = 'merged_taxon_id') newtax where taxonomy_counts.genome_id = newtax.genome_id;

# Create helper table for the "where to stop, what to call it" data.
# id here is a taxon id. ensembl_taxon_name is whatever should be displayed.
drop table if exists tax_stop_levels;
create table tax_stop_levels (taxon_id int, ord int, name text, ensembl_taxon_name text);

# insert the desired stopping taxon ids and names
insert into tax_stop_levels (taxon_id, name) (
  select taxon_id, lower(name) from ncbi_taxa_name where lower(name) in (
    'root',
    'archaea',
    'bacteria',
    'fungi',
    'metazoa',
    'viridiplantae'
) and name_class = 'scientific name');

# insert the desired display names for each entry
update tax_stop_levels set ensembl_taxon_name = 'Animals', ord = 1 where name = 'metazoa';
update tax_stop_levels set ensembl_taxon_name = 'Archaea', ord = 2 where name = 'archaea';
update tax_stop_levels set ensembl_taxon_name = 'Bacteria' , ord = 3 where name = 'bacteria';
update tax_stop_levels set ensembl_taxon_name = 'Fungi', ord = 4 where name = 'fungi';
update tax_stop_levels set ensembl_taxon_name = 'Green Plants', ord = 5 where name = 'viridiplantae';
update tax_stop_levels set ensembl_taxon_name = 'Others', ord = 6 where name = 'root';

# create the macro that does the magic
drop macro if exists uptax;
create macro uptax (tax_id) as (with recursive find_tax (lvl, pt_id) as (
  select 0, parent_id from ncbi_taxa_node where taxon_id = tax_id
  union all
  select lvl + 1, parent_id from find_tax ft inner join ncbi_taxa_node ntn on ft.pt_id = ntn.taxon_id where ntn.taxon_id not in (select taxon_id from tax_stop_levels))
select pt_id from find_tax order by lvl desc limit 1);

# Create the actual counts data. Runs the macro on each species.
update taxonomy_counts set domain_tax_id = uptax(taxonomy_id);


drop table if exists genome_taxonomy_counts;
create table genome_taxonomy_counts as select tc.release_id, label, tsl.taxon_id, ensembl_taxon_name, count(ifnull(domain_tax_id, 0)) as 'count', ord from taxonomy_counts tc
    inner join tax_stop_levels tsl on tc.domain_tax_id = tsl.taxon_id left join ensembl_release er on er.release_id = tc.release_id
    group by tc.release_id, label, ord, ensembl_taxon_name, tsl.taxon_id
    order by tc.release_id, ord asc;
update genome_taxonomy_counts set label = '' where label is null;


# View result
.print ''
select sum(count) as Total from genome_taxonomy_counts where release_id = 0;
.print 'Created table genome_taxonomy_counts. Across all releases:'
.print ''
from genome_taxonomy_counts where release_id = 0 order by ord;
.print ''
.print 'Per release:'
.print ''
from genome_taxonomy_counts where release_id > 0 order by release_id,ord;

#drop table taxonomy_counts;
drop table tax_stop_levels;
drop macro uptax;
