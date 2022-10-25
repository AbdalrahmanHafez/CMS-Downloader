import json
import os


class Printer:
    def __init__(self):
        self.data = {}
        self.PIPE = "│"
        self.ELBOW = "└──"
        self.TEE = "├──"
        self.PIPE_PREFIX = "│   "
        self.SPACE_PREFIX = "    "
        
    def addKey(self, key):
        if(key in self.data):
            return
        self.data[key] = []

    def addValue(self, key, value, desc=""):
        # insert the value in the correct place
        self.data[key].append({"name": value, "desc": desc})
        
    
    def display(self):
        os.system('cls||clear')
        for key, value in self.data.items():
            print(f"{self.PIPE} {key}")
            for item in value:
                name = item["name"]
                desc = item["desc"]
                print(f"{self.TEE} {name}" + (f" ({desc})" if desc else ""))

        # return json.dumps(self.data, sort_keys=True, indent=4)



def example():
    p = Printer()
    p.addKey("HCI")
    p.addValue("HCI", "File 1.pdf", "Description 1")
    p.addValue("HCI", "File 2.pdf")
    p.addValue("HCI", "File 3.pdf")

    p.addKey("AI")
    p.addValue("AI", "AI Lecture 3.mp4")
    p.addValue("AI", "Ai Lecture 1.pdf")

    p.addKey("Test")

    p.display()


# example()