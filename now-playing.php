<?php
$command = "python /usr/local/bin/myriad-nowplaying/getnowplaying.py -f /mnt/PSquared/Audiowall/0000s/Tagged";
$output = shell_exec($command);

header("Content-Type: text/plain");

if($output == NULL){
    echo "Halton Community Radio, 92.3 FM";
} else {
    echo $output;
}
?>