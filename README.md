# Introduction #

This is a simple utility for exporting Crates in Mixxx to an XML file. It will
also load these same XML files into a Mixxx Library.

# How to Run #

By default, crateport will output the generated XML file to standard input
(the screen). Just call it like so:

> bash$ crateport.py

To output the crate XML to a file, just pass the file name as the first
parameter.

> bash$ crateport.py output.xml

If, for some reason you need to explicitly set crateport to export mode you
can use the option flag '-e' or '--export', ie:

> bash$ crateport.py --export output.xml

To load the crate into the Mixxx Library, use the '-i- or '--import' option:

> bash$ crateport.py --import output.xml

You can also specify a different Mixxx Library Database File using the '-d' or
'--dbname' flag.

> bash$ crateport.py --dbname mixxxdb.sqlite.backup output.xml

If not set explicitly it will use the default Mixxx Library location for your
platform.

