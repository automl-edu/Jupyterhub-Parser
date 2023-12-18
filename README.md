## Bias Script Docs

Please make sure before running the scripts to install the requirements:

    pip install -r requirements.txt

### Exporting Mails in Batches

Change the current working directory to `./bias/mail_export` you'll see the script `main.py`. Run the script with the following command:

    python main.py roster_file

The script will then print out the mails in batches of 50. The script has additional options:

```md
    positional arguments:
    roster_file     The path to the file of the course roster as csv

    options:
    -h, --help      show this help message and exit
    -o, --output    The path to the output file
    -n              The batch size of the mails
```

### Parsing the Data

#### Step 1

Add all the files you get from bias to an **empty** folder of your choosing. The importaant part is that you put them all in the same folder and that they end with *.pdf.

#### Step 2

Change the current working directory to `./bias/parse_data` you'll see the script `main.py`. Run the script with the following command:

    python main.py roster_file bias_path merge_file

The script will then merge the roster file with the corresponding username and password from the bias files using the merge_file. Then it will ask you if you want to send the mails directly to the students. By hitting y and enter the script will send the mails to the students.  
Running the Script for the first time will create a `secrets.json` file in the current working directory. It is also filled with plausible defaults. You just have to add your mail address and password.

The script has additional options:

```md
    positional arguments:
    roster_file             The path to the file of the course roster in csv
    bias_path               The path to the folder containing the Bias PDFs
    merge_file              The path to the file containing the merge data

    options:
    -h, --help              show this help message and exit
    -c, --config            The path to the config file
    -o, --output            The path to the output folder
```
