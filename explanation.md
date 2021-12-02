# (What is wrong with) Table structure
The nutrient can be on the same depth as the values and units
The values can come after the units, or not at all or the units between (), separated by a / like
5 gram / (2 kg)
gram 5 / ml 10

Per data could be in a separate head or with the nutrients and values itself.
Per data could be all in a separate head or at the top or spread out through the table.
An assumption that however can be made is that the first per can be linked to the first value/unit and the second to the second.
In very very very very very rare cases this is not possible.

There is plain text also on the depth of the values and units and nutrients
Assuming a nutrient is always on a specific i within the parsed data, can turn into faulty data

Not normalizing the data as in, making all the nutrient names equal, if not, it will be harder to do things with the data later.
Yes this means that spelling mistakes are harder to track but you can implement a check on a percentages to get rid of them.
Question is if clean data with a low percentage missing data is a better choice than always data but not clean

Prepared data (If the information is about a prepared product or unprepared product) is the worst of all.
It can be at the top next to the Each 100ml data or before it. Could be for all the Each 100ml Each 250ml or just for one.
It can be at the bottom or if the structure is "Per 100 ml, nutrients, per 250 ml, unpreprared, nutrients", it only belongs to the second information
Where Each/Per data is located and where the Prepared data is located and how deep.