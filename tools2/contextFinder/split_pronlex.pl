#!usr/bin/perl -w
######################################################################
# split pronlex into smaller sections!
# written by rc 07.25.01 to more efficiently search pronlex
# in contextFinder.pl
######################################################################


$pronlex = "pronlex.txt";
    	    # open PRONLEX dictionary file and read in 
open (PRONLEX, "<$pronlex") or die("\nfailure to open Pronlex: $!\n");
do                                           # get rid of preamble
{			
    $entry = <PRONLEX>;
} while ( $entry =~ /^#/);  
	
$ac = "pronlex_A-C.txt";     
open (PAC, ">>$ac") || die "\nfailure to open A-C file: $!\n";
$dh = "pronlex_D-H.txt";     
open (PDH, ">>$dh") || die "\nfailure to open D-H file: $!\n";
$io = "pronlex_I-O.txt";    
open (PIO, ">>$io") || die "\nfailure to open I-O file: $!\n";
$ps = "pronlex_P-S.txt";    
open (PPS, ">>$ps") || die "\nfailure to open P-S file: $!\n";
$tz = "pronlex_T-Z.txt";    
open (PTZ, ">>$tz") || die "\nfailure to open T-Z file: $!\n";



while ($entry = <PRONLEX>) 
{ 

    if ($entry =~ /^[a-cA-C]/)
    {
	print PAC "$entry";
    }
    elsif ($entry =~ /^[d-hD-H]/)
    {
	print PDH "$entry";
    }
    elsif ($entry =~ /^[i-oI-O]/)
    {
	print PIO "$entry";
    }
    elsif ($entry =~ /^[p-sP-S]/)
    {
	print PPS "$entry";
    }
    elsif ($entry =~ /^[t-zT-Z]/)
    {
	print PTZ "$entry";
    }
}

close (PRONLEX);
close (PAC);
close (PDH);
close (PIO);
close (PPS);
close (PTZ);
