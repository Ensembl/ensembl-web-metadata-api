use Net::FTP;
  
#my $ftp = Net::FTP->new("ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr22.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz");
my $ftp = Net::FTP->new("http://ftp.1000genomes.ebi.ac.uk", Debug => 2); 
#my $ftp = Net::FTP->new("ftp://ftp.ngdc.noaa.gov/", Debug => 2);
print ("Testing FTP : \n", $ftp, "\n");
$ftp->login();
