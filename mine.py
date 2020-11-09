'''Mines websites for attributes of interest.'''
import prospectors
import utils
import sys
import constants

from multiprocessing import Process


def mine_website(site_name, export_filetype='csv'):
    config = utils.load_website_config(site_name)
    prospector = getattr(prospectors, config['prospector_class'])(site_name)
    prospector.mine()
    utils.refine_ore(prospector.ore_cart, export_filetype=export_filetype)



if __name__ == '__main__':
    if not sys.argv[1]:
        print('Must pass a website name! See "website_config.json" for valid site names')
    else:
        for filetype in constants.VALID_ORE_EXPORT_TYPES:
            print(filetype)
            p = Process(target=mine_website, args=(sys.argv[1], filetype))
            p.start()
        # site_name_1 = sys.argv[1]
        # site_name_2 = sys.argv[2]
        # p1 = Process(target=mine_website, args=(site_name_1, ))
        # p2 = Process(target = mine_website, args=(site_name_2, ))
        # p1.start()
        # p2.start()
        # print('helllo')