#!/usr/bin/env python

import sys
import pprint

from inputHandling.parser import parser
from inputHandling.validate import validate
from inputHandling.accounts import accounts

pp = pprint.PrettyPrinter(indent=4)

def main():
    args = parser().parse_args()
    validate(args)
    account = accounts(args.accounts)

    pp.pprint(account[0]['arn'])



if __name__ == "__main__":
    try:
        main()
    except Exception as inst:
        print(type(inst))
        print(inst)
        sys.exit(-1)
