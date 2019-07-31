from gooey import Gooey, GooeyParser
import argparse

@Gooey(program_name='some program')
def main():
    # Top level parser defines the whole window
    topparser = GooeyParser(description='Some words', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # add_subparsers method is an object that allows you to add individual parsers (a parser parser)
    # the add paprser object will always be the key with the value being the parser that is interpreted.
    someparsers = topparser.add_subparsers(dest='someplace')

    # each subparser will be an option on the Left column
    subparser1 = someparsers.add_parser('someoption')
    # add_argument_group is organizational and allows for a nice help window
    croc_facts = subparser1.add_argument_group(
        'Just Crocodile Things',
        description='There are 13 species of crocodiles, so there are many different \n' +
                    'sizes of crocodile. The smallest crocodile is the dwarf crocodile. \n' +
                    'It grows to about 5.6 feet (1.7 meters) in length and weighs 13 to \n'
                    '15 pounds '
    )
    # regardless of if the arguments are in groups or not they still return at the top level of the arg dictionary
    someoption = croc_facts.add_argument('-somecrocodile', action='store_true', help='Nothing to see here, move along.')


    subparser2 = someparsers.add_parser('someotheroption', help='foo',)
    test_arg = subparser2.add_argument('-someotherarg', help='bar')

    # Will only parse the args on the active page when the user presses start good for mutually exclusive arguments
    # like a separate menu for loading a previous save
    args = topparser.parse_args()

    print(args)


if __name__ == '__main__':
    main()