class ModelTimedoutException(Exception):
    
    def __init__(self, *args: object) -> None:
        '''The model timed out.'''
        super().__init__(*args)

class ToolUseUnsupported(Exception):
    def __init__(self, *args: object) -> None:
        '''The tool is not supported.'''
        super().__init__(*args)