# DialogFlow-Intent-Manager

DialogFlow-Intent-Manager is a script written in Python that allows you to create/delete intents from exported intent files.

### Table of Contents

- [Usage](#usage)
  - [Creating Intents (option 1)](#creating-intents-option-1)
  - [Deleting Intents (option 2)](#deleting-intents-option-2)

---

### Usage

To run this script you need to have a service account JSON key. if you don't have one, watch [this video](https://youtu.be/Zp-KHSDaFk8) that shows how to create one.

Once you have a service account JSON key, rename it to `authorization.json` and place it in the same directory as this script. If you want to change the name from `authorization.json` to something else, you can do it in the `config.json` file.

You also need to place the exported intent files in the `./intents` folder.<br>
After that you can run the script with the following command:

```
python3 -m pip install -r requirements.txt
python3 main.py
```

#### Creating Intents (option 1)

After selecting option 1, the script will ask you to make sure that you have added the exported intents to the `./intents` folder.<br>
If you have, press `Enter` to create intents.

You might see something like `SKIPPED, alreadyexists` in the console. This means that the intent with that name already exists in your DialogFlow agent.<br>
You might also see something like `FAIL, Reason: [reason]`, this means that the intent couldn't be created and it will give you a reason to why it failed. If you can't figure out why it couldn't be created, please create an [issue](https://github.com/InimicalPart/DialogFlow-Intent-Manager/issues/new) on GitHub.

#### Deleting Intents (option 2)

After selecting option 2, the script will ask you to make sure that you have added the exported intents to the `./intents` folder.<br>
If you have, press `Enter` to start deleting intents.

You might see something like `SKIPPED, doesntexist` in the console. This means that the intent with that name doesn't exist.<br>
You might also see something like `FAIL, Reason: [reason]`, this means that the intent couldn't be deleted and it will give you a reason to why it couldn't be deleted. If you can't figure out why it couldn't be deleted, please create an [issue](https://github.com/InimicalPart/DialogFlow-Intent-Manager/issues/new) on GitHub.

---

### Automating the process

If you are planning to use this in a script, you might want to skip the interactive part and automate the process. You can do this by adding switches like `--create/-c` or `--delete/-d` when running the script. You can also specify the where the intents are located using `--intents-folder/-i`. If you don't like the default path to the authorization file or the name to it, you can use `--authorization-path/-a` to specify a path where the JSON key is located. Here is an example of how to do it:

```
python3 main.py -c -i C:\this\is\a\directory\intents -a C:\this\is\a\directory\authorization.json -p myAI
```

**NOTE:** When using the `--intents-folder/-i` switch, the script will create a `done` folder inside of the specified folder, it will also create a `bkup` folder if the switch for backing up intents is specified.

If both `--create` and `--delete` are not specified, the script will proceed with the interactive part.

If `--project-id/-p` and `--authorization-path/-a` are specified, the script will not look for `config.json` and will use the values specified.

To see all switches and get a description of them, run the script with the `--help/-h` switch.
