# Information

WARNING: This program is purely for demonstration and not intended for distribution. Per Reverso's Condition of Use (https://www.reverso.net/disclaimer.aspx?lang=EN) you must use Reverso's original site on a regular web browser. After you are done using this app, please uninstall and remove from your system.

# Guide

Use Python3 to execute the main file.

```$ python3 dict_crawler.py```

You will receive an input prompt consisting of three arrows ```>>> ```

Type in a French word to retrieve its definition.

To enter a sentence that you want to export to CSV, first type ```sss``` and type in the senetence you would like to save. Surround unknown words with double paranthesis ```((``` and ```))``` . If the word is a conjugated verb, you can place a ```|``` after the word within the paranthesis, and type in the root verb.

e.g. 
```>>> sss Dans les rues, la nuit, au lieu des pâles luminaires, ((brillaient|briller)) des lampes électriques```

This will retrieve the definition for ```briller``` instead of ```brillaient```.

Type ```exit``` or ```quit``` once you are done, and a CSV file containing all the sentences you saved along with the word definitions will be exported to the ```anki_sentences```folder.

# Demonstration

![Alt text](./Capture%20d’écran,%20le%202021-05-26%20à%2019.31.46.png "Demonstration")
