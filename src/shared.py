# Todo: Most of this code is copy-pasted from two private, in-dev projects. To be replaced with the PyPI package I'll make some day
import json


class Config:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.dictionary = {}
        self.read_file()

    def read_file(self) -> None:
        with open(self.file_name) as f:
            self.dictionary = json.load(f)

    def write_file(self) -> None:
        with open(f"{self.file_name}", "w") as f:
            f.write(json.dumps(self.dictionary))  # User-friendly? Who do you think I am?

    def read(self, *keys: str | list[str]) -> any:
        current_level = self.dictionary
        for key in keys:
            current_level = current_level.get(key, {})  # Default cannot be None, since it doesn't have a get method
        return current_level

    def write(self, value: any, *keys: str | list[str]) -> None:
        current_level = self.dictionary
        for key in keys[:-1]:
            current_level = current_level.setdefault(key, {})
        current_level[keys[-1]] = value
        self.write_file()

    def delete(self, *keys: str | list[str]):
        # Written by ChatGPT
        current_level = self.dictionary
        for key in keys[:-1]:
            current_level = current_level.get(key, {})

        last_key = keys[-1]
        if last_key in current_level:
            del current_level[last_key]
            self.write_file()


def sinput(prompt: object = "", sep: object = " ", end: object = ">>", mode: str = None) -> input:
    match mode:
        case "compare":
            return input(f"{prompt}{sep}{end}").casefold().strip()
        case "interrupt":
            if prompt == "":
                prompt = "Press Enter to continue."
            return input(f"{prompt}{sep}{end}")
        case _:
            return input(f"{prompt}{sep}{end}")
