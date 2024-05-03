class Parameter(dict):
    def __init__(self, default, options=None):
        self.default = default
        self.options = options or []
        super().__init__({
            "default": default,
            "options": options,
        })
