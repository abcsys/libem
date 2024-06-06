import libem


def positive():
    e1 = "mighty freedom gundam"
    e2 = "ZGMF/A-262PD-P"
    
    libem.LIBEM_LOG_LEVEL = 0

    is_match = libem.match(e1, e2)

    print(f"Entity 1: {e1}\nEntity 2: {e2}\n"
          f"Match: {is_match}")


if __name__ == '__main__':
    positive()
