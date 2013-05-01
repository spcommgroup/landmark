#!/usr/bin/perl

print "This program looks for the times for any given phoneme in a specified file\n";
print "11/29/01 NMV\n"; 

print "What is the name of the file you want to check? (e.g. k11_mjx.label)\n";
$infile = <STDIN>;

open (CHECK, "<".$infile) or die("$!, stopped");
@lines =<CHECK>;
close(CHECK);
print "\n\n"; 

print "What is the name of the phone? (e.g. ae)\n";
$phone = <STDIN>;

$end = @lines;
for ($i=0; $i <$end; $i++){
	if ($lines[$i] =~ /Symbol: $phone/){
		print "this line" . $lines[$i]; 
	#	$timeInd = index($line,@lines)-1 ;
		print "\t\t\t" .$lines[$i-1] . "\n";
	}
} 

