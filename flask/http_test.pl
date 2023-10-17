use File::HTTP qw(:open);

open(my $fh, '<', 'http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz') or die $!;

print ($fh, "\n");

