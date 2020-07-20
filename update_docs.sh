# Update Github pages
$HOME/.local/bin/kb4it -source basico/data/help/sources/ -target docs/ -log DEBUG -force

# Update Basico Help Center
$HOME/.local/bin/kb4it -source basico/data/help/sources/ -target basico/data/help/html/ -log DEBUG -force
