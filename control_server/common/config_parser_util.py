# encoding: utf8
import ConfigParser



def get(parser, section, option, default=None):
    try:
        return parser.get(section, option)
    except ConfigParser.NoOptionError:
        return default  



def getint(parser, section, option, default=None):
    try:
        return parser.getint(section, option)
    except ConfigParser.NoOptionError:
        return default  






