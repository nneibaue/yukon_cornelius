'''Mines websites for attributes of interest.'''
import prospectors
import utils
import sys
import constants
import yaml

from multiprocessing import Process


def mine_website(site_name, export_filetype='csv'):
    config = utils.load_website_config(site_name)
    prospector = getattr(prospectors, config['prospector_class'])(site_name)
    prospector.mine()
    utils.refine_ore(prospector.ore_cart, export_filetype=export_filetype)

def run_from_yaml_config(config_file):
    with open(config_file, 'r') as f:
        run_config = yaml.load(f, Loader=yaml.Loader)

    print(run_config)
    for website in run_config['websites']:
        p = Process(target=mine_website,
                    args=(website, run_config['websites'][website]['filetype']))
        p.start()


if __name__ == '__main__':
    if not sys.argv[1]:
        print('Must pass a website name or yaml config!')
    else:
        arg = sys.argv[1]
        if arg.endswith('yml'):
            run_from_yaml_config(arg)
        else:
            mine_website(arg, export_filetype='csv')