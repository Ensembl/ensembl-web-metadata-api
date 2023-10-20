from loguru import logger

def parse_region_input(rgn: str) -> bool:
    try:
        rn, coords = rgn.split(":")
        start, end = coords.split("-")
        return (rn, start, end)
    except Exception as ex:
    	logger.debug(ex)
    return None



if __name__ == "__main__":
    valid_input = "1:123-456"
    valid_op = parse_region_input(valid_input)
    print (valid_op)

    invalid_input = "123-456"
    invalid_op = parse_region_input(invalid_input)
    print (invalid_op)