

This code aims to be a library for parsing Orba2 artipreset files
It uses existing artipreset file as a template, loading it via xmltodict as a dict, and 
then, from this dict - recursively generating an object structure that represents Orba2 preset
Each type of element in the artipreset has it's own class.

This allows to add  methods to these classes, and autocomplete properties.

Class properties are used only for autocomplete functions anyway,  they are not verified, as properties would be added on the fly if added.

Unfortunately, as soon as Orba2 does not follow any naming convention in naming xml attributes,
it is not possible to convert tham to python's snake_case and back,  therefore only elements appear as snake_case in objects.
Object properties, storing attribute values, are named exactly as attributes in xml.



known differences from the original artipreset files
that I've found out when doing roundtrip parsing/unparsing:

 xml header  becomes  downcase:   

<?xml version="1.0" encoding="UTF-8"?>     
->  
<?xml version="1.0" encoding="utf-8"?>

xmltodict uses full closing tag instead of the shorthand:

<PatternEntry name="" patternData="" patternDuration="0"/> 
  -> 
<PatternEntry name="" patternData="" patternDuration="0"></PatternEntry>


due to uneven behavior between xmltodict.parse and xmltodict.unparse,
&#8211; symbol (en dash) used in a couple of original presets is exported incorrectly.
https://github.com/martinblech/xmltodict/issues/317
I replace it with a regular dash, and most probably using other html/xml escaped charactes in xml attributes will lead to failure
