from typing import NoReturn

class Memory:
    def __init__(self) -> NoReturn:
        self.memory = []
        
    def set_memory(self, ques: str, ans: str) -> None:
        self.memory.append((ques, ans))
        
    def get_memory(self) -> list[str]:
        return self.memory