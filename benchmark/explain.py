import libem

e1 = {
    "title": "hoyle card games 2007",
    "manufacturer": "encore software",
    "price": 29.99
}

e2 = {
    "title": "encore software 10025 hoyle card games ( win 98 me 2000 xp )",
    "manufacturer": None,
    "price": 7.47
}

libem.LIBEM_LOG_LEVEL = 0  # debug
libem.calibrate({
    "libem.match.parameter.tools": [],  # turn off browse etc.
})
libem.calibrate({"libem.match.prompt.output":
                     "Explain your answer step by step and end with 'yes' or 'no' only."})
libem.match(e1, e2)
